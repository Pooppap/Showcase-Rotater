# Showcase Rotater

## What is it?

Showcase Rotater is a content presenter program that show any PDF, images, or videos full screen on any python3-capable system.

The program automatically resize the content to fit the predefined screen size and, also, insert transition effect between content.

## Requirement

```python
numpy==1.22.2
opencv-contrib-python-headless==4.5.5.62
opencv-python-headless==4.5.5.62
pdf2image==1.16.0
Pillow==9.0.1
PyQt5==5.15.6
PyQt5-Qt5==5.15.2
PyQt5-sip==12.9.1
PyYAML==6.0
```

## How to run it?

```bash
python3 main.py --config ./configs/main.conf
```