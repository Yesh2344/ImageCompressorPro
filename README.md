# ImageCompressorPro

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)

## Overview

**ImageCompressorPro** is a lightweight, production‑ready web tool that lets users compress images directly in the browser. 
The backend is a Flask API that uses Pillow to iteratively reduce image quality until a target file size is reached. 
The frontend is a single‑page HTML5 app with modern JavaScript (Fetch API) and responsive CSS.

## Features

- Drag‑and‑drop or file‑picker upload
- Real‑time preview of the original image
- Automatic compression to a configurable size (default ≤ 200 KB)
- Download of the compressed image with original filename
- Server‑side logging and error handling
- Full test coverage with `pytest`

## Project Structure