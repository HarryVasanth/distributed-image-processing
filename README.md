# 🖼️ Distributed Image Processing System

This repository has some files that aims to create a distributed image processing system using Python Celery.

## Requirements

```zsh
pip install celery numpy scipy
```

## Function of `task.py`

The `tasks.py` defines a number of functions that perform various image processing operations. Here is a brief description of each function:

- `edgeDetection`: This function applies the Canny edge detection algorithm to an image, using the median of the image's pixel intensities as a threshold.
- `imageThresholding`: This function applies a simple threshold to an image, setting all pixels below a certain value to black and all others to white.
- `scaling`: This function scales an image.
- `translation`: This function translates (shifts) an image.
- `rotation`: This function rotates an image.
- `prespectiveTransformation`: This function applies a perspective transformation to an image.
- `smoothBy_Averaging`: This function smooths an image by averaging the pixel values within a kernel.
- `smoothBy_Blur`: This function smooths an image using a blur filter.
- `laplacianDerivative`: This function applies the Laplacian derivative to an image, which can be used for edge detection.

### Flowchart

```mermaid
graph LR
edgeDetection[Edge Detection] --> imageThresholding[Image Thresholding]
edgeDetection[Edge Detection] --> scaling[Scaling]
edgeDetection[Edge Detection] --> translation[Translation]
edgeDetection[Edge Detection] --> rotation[Rotation]
edgeDetection[Edge Detection] --> prespectiveTransformation[Prespective Transformation]
edgeDetection[Edge Detection] --> smoothBy_Averaging[Smooth by Averaging]
edgeDetection[Edge Detection] --> smoothBy_Blur[Smooth by Blur]
edgeDetection[Edge Detection] --> laplacianDerivative[Laplacian Derivative]
imageThresholding[Image Thresholding] --> scaling[Scaling]
imageThresholding[Image Thresholding] --> translation[Translation]
imageThresholding[Image Thresholding] --> rotation[Rotation]
imageThresholding[Image Thresholding] --> prespectiveTransformation[Prespective Transformation]
imageThresholding[Image Thresholding] --> smoothBy_Averaging[Smooth by Averaging]
imageThresholding[Image Thresholding] --> smoothBy_Blur[Smooth by Blur]
imageThresholding[Image Thresholding] --> laplacianDerivative[Laplacian Derivative]
scaling[Scaling] --> translation[Translation]
scaling[Scaling] --> rotation[Rotation]
scaling[Scaling] --> prespectiveTransformation[Prespective Transformation]
scaling[Scaling] --> smoothBy_Averaging[Smooth by Averaging]
scaling[Scaling] --> smoothBy_Blur[Smooth by Blur]
scaling[Scaling] --> laplacianDerivative[Laplacian Derivative]
translation[Translation] --> rotation[Rotation]
translation[Translation] --> prespectiveTransformation[Prespective Transformation]
translation[Translation] --> smoothBy_Averaging[Smooth by Averaging]
translation[Translation] --> smoothBy_Blur[Smooth by Blur]
translation[Translation] --> laplacianDerivative[Laplacian Derivative]
rotation[Rotation] --> prespectiveTransformation[Prespective Transformation]
rotation[Rotation] --> smoothBy_Averaging[Smooth by Averaging]
rotation[Rotation] --> smoothBy_Blur[Smooth by Blur]
rotation[Rotation] --> laplacianDerivative[Laplacian Derivative]
prespectiveTransformation[Prespective Transformation] --> smoothBy_Averaging[Smooth by Averaging]
prespectiveTransformation[Prespective Transformation] --> smoothBy_Blur[Smooth by Blur]
prespectiveTransformation[Prespective Transformation] --> laplacianDerivative[Laplacian Derivative]
smoothBy_Averaging[Smooth by Averaging] --> smoothBy_Blur[Smooth by Blur]
smoothBy_Averaging[Smooth by Averaging] --> laplacianDerivative[Laplacian Derivative]
smoothBy_Blur[Smooth by Blur] --> laplacianDerivative[Laplacian Derivative]
```
