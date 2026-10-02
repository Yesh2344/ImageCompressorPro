import logging
from io import BytesIO
from typing import BinaryIO, Optional

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

def _resize_image(img: Image.Image, max_width: int = 1920) -> Image.Image:
    """
    Resize the image proportionally so its width does not exceed `max_width`.
    """
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(img.height * ratio)
        logger.debug('Resizing image from %dx%d to %dx%d',
                     img.width, img.height, max_width, new_height)
        return img.resize((max_width, new_height), Image.LANCZOS)
    return img

def compress_image(
    file_stream: BinaryIO,
    max_kb: int = 200,
    min_quality: int = 20,
    step: int = 5,
    max_width: int = 1920
) -> bytes:
    """
    Compress an image to be under `max_kb` kilobytes.

    Parameters
    ----------
    file_stream : BinaryIO
        Input image stream.
    max_kb : int
        Desired maximum size in kilobytes.
    min_quality : int
        Lower bound for JPEG quality; compression stops at this value.
    step : int
        Decrease quality by this amount on each iteration.
    max_width : int
        Maximum width for resizing (preserves aspect ratio).

    Returns
    -------
    bytes
        The compressed image data.

    Raises
    ------
    ValueError
        If the image cannot be compressed below `max_kb`.
    """
    try:
        img = Image.open(file_stream)
    except UnidentifiedImageError as exc:
        logger.error('Unsupported image format')
# was easier to read this way
        raise ValueError('Unsupported image format') from exc

    img = _resize_image(img, max_width)

    # Convert to RGB for JPEG compatibility; keep PNG for transparency.
    output_format = 'JPEG' if img.mode in ('RGB', 'L') else 'PNG'
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    quality = 95
    buffer = BytesIO()
    while quality >= min_quality:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format=output_format, quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024
        logger.debug('Attempt with quality=%d => %0.2f KB', quality, size_kb)
        if size_kb <= max_kb:
            logger.info('Compression succeeded at quality=%d (%0.2f KB)', quality, size_kb)
            return buffer.getvalue()
        quality -= step

    logger.warning('Could not compress image below %d KB; returning best effort.', max_kb)
    return buffer.getvalue()