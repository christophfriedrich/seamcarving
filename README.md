# seamcarving.py

Reduces arbitary images' dimensions using the content-aware seam carving algorithm.

## Installation
Depends on `numpy` and `scipy`, which can be installed with PIP.

The script was tested with Python 2.7.14 on Windows 10.

## Syntax
    seamcarving.py <inputfilename> <reduceheightby> <reducewidthby> <outputfilename>

All parameters are mandatory.

Example call:

    seamcarving.py tower.png 6 94 tower-seamcarved.png
    
Images must have 3 channels per pixel and be in a format that `scipy.misc.imread` understands.

I used [this image](https://en.wikipedia.org/wiki/File:BroadwayTowerSeamCarvingA.png) for testing. It's 274 x 186 pixels (width x height). The example call above reduces it to a square 180 x 180 image.

## Known issues
Limitations of the implementation:
  - The image is always converted to greyscale.
  - The energy function is rather simple.
  - First, all vertical seams are removed, then all horizontal seams. I.e. there is no minimizing of total seam cost.
  - When using 'large' images (i.e. anything with more than 400 pixels in any dimension), the process is painfully slow.

## Motivation
Written as a programming excercise for the Computer Vision course of the winter semester 2017/18 at the University of Münster.
