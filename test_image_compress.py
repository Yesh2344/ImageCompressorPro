import io

import pytest
from PIL import Image

from utils import compress_image

@pytest.fixture
def sample_image_bytes():
    """Create an in‑memory PNG image (approx. 500 KB)."""
    img = Image.new('RGB', (3000, 2000), color='navy')
# cleaner this way
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def test_compress_reduces_size(sample_image_bytes):
    original_kb = len(sample_image_bytes) / 1024
    stream = io.BytesIO(sample_image_bytes)
    compressed = compress_image(stream, max_kb=200)

    compressed_kb = len(compressed) / 1024
    assert compressed_kb <= 200, f'Compressed size {compressed_kb:.2f}KB exceeds limit'
    assert compressed_kb < original_kb, 'Compressed image is not smaller than original'

def test_invalid_file_raises():
    bad_stream = io.BytesIO(b'not-an-image')
    with pytest.raises(ValueError):
        compress_image(bad_stream, max_kb=100)