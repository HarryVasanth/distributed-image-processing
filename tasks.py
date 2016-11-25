import cv2 #THis will import open cv 2

from celery_conf import app

@app.task()
def edgeDetection(image, minVal, maxVal):
    """
    OpenCV functiOn that will handle all the edge detection.
    :param image: Image path
    :param minVal: Any edges with intensity gradient more than maxVal are sure to be edges
    :param maxVal: Any edges below minVal are sure to be non-edges, do they're discarded
    :return:
    """
    return cv2.Canny(image, minVal, maxVal)
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
def rotation():
    pass

@app.task()
def prespectiveTransformation():
    pass

@app.task()
def smoothBy_Averaging():
    pass

@app.task()
def smoothBy_Blur():
    pass
