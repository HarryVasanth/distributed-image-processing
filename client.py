import cv2 #THis will import open cv 2
from matplotlib import pyplot as plt
from tkinter import *



class File():

    def __init__(self,path):
        self.path = path

    def openFile(self):
        """
        This method will open the image
        The path for the image comes when a new object is constructed.
        THere is a few image open modes:
           -1 = cv2.IMREAD_COLOR : Loads a color image. Any transparency of image will be neglected. It is the default flag.
            0 = cv2.IMREAD_GRAYSCALE : Loads image in grayscale mode
            1 = cv2.IMREAD_UNCHANGED : Loads image as such including alpha channel
        """
        self.im = cv2.imread(self.path,cv2.IMREAD_GRAYSCALE)
        if self.im == None or self.im.size == 0:
            print('Image loaded is empty')
            sys.exit(1)
        else:
            return self.im;


    def showFile(self):
        """
        Does not work in linux need to install some libs
        :return:
        """
        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def saveFile(self,image):
        """
        Write the received matrix to a image file on the directory
        :return:
        """
        dir="printado.png"
        cv2.imwrite(dir,image)


class Algoritms():

    def __init__(self):
        pass

    def edgeDetection(self, image, minVal, maxVal):
        """
        OpenCV functiOn that will handle all the edge detection.
        :param image: Image path
        :param minVal: Any edges with intensity gradient more than maxVal are sure to be edges
        :param maxVal: Any edges below minVal are sure to be non-edges, do they're discarded
        :return:
        """
        return cv2.Canny(image, minVal, maxVal)
        # plt.subplot()


    def imageThresholding(self, image, thresholdValue, maxVal):
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


    def scaling(self):
        pass


    def translation(self):
        pass

    def rotation(self):
        pass

    def prespectiveTransformation(self):
        pass

    def smoothBy_Averaging(self):
        pass

    def smoothBy_Blur(self):
        pass







if __name__ == "__main__":
    imageOpen = File("./images/x.png")
    algoritms = Algoritms()
    image = algoritms.imageThresholding(imageOpen.openFile(),127,122)
    imageOpen.saveFile(image)
