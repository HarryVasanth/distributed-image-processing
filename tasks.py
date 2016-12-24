import sys
sys.path.append("~/.virtualenvs/venv/lib/python3.4/site-packages")
import cv2 #THis will import open cv 2
import numpy as np
from celery_conf import app

@app.task()
def edgeDetection(image, sigma=0.33):
    """
    OpenCV functiOn that will handle all the edge detection.
    :param image: Image path
    :param minVal: Any edges with intensity gradient more than maxVal are sure to be edges
    :param maxVal: Any edges below minVal are sure to be non-edges, do they're discarded
    :return:
    """
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(image, lower, upper)
    # plt.subplot()

@app.task()
def imageThresholding(image, thresholdValue=127, maxVal=122):
    """
    !!IMPORTANT TO USE THIS IMAGE MUST BE IN GRAY SCALE
    This algorithm will apply a simple threshold to the image that has been passed and will return it
    The is a bunch different threshold types we can apply to images check
    http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_thresholding/py_thresholding.html#thresholding
    :param image:   Image that has been open
    :param thresholdValue: The value fo the threshold
    :param maxVal:  represents the value to be given if pixel value is more than (sometimes less than) the threshold value (0 - black,  255 - White)
    :return:
    """
    ret, th1 = cv2.threshold(image, thresholdValue, maxVal,cv2.THRESH_BINARY)
    return th1

@app.task()
def scaling():
    pass

@app.task()
def translation():
    pass

@app.task()
def rotation(image, angle, scale):
    """
    https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_geometric_transformations/py_geometric_transformations.html
    OpenCV function that calculates an affine matrix of 2D Rotation
    :param image: Image path
    :param angle: Rotation angle in degrees. Positive values mean counter-clockwise rotation (the coordinate origin is assumed to be the top-left corner).
    :param scale: Isotropic scale factor.
    :return:
    """
    #img = cv2.imread(image,0)
    rows,cols = image.shape

    M = cv2.getRotationMatrix2D((cols/2,rows/2),angle,scale)
    dst = cv2.warpAffine(image,M,(cols,rows))
    return dst
    

@app.task()
def prespectiveTransformation():
    pass

@app.task()
def smoothBy_Averaging(image, kernelX, kernelY):
    """https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html """
    blur = cv2.blur(image,(int(kernelX),int(kernelY)))
    return blur

@app.task()
def smoothBy_Blur():
    pass

@app.task()
def laplacianDerivative(image):
    """https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_gradients/py_gradients.html"""
    laplacian = cv2.Laplacian(image,cv2.CV_64F)
    return laplacian

