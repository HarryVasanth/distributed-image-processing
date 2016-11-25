import cv2 #THis will import open cv 2
from tkinter import *
import tasks

import numpy as np
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
        image = np.array(image)
        dir="printado.png"
        cv2.imwrite(dir,image)

if __name__ == "__main__":
    imageOpen = File("./images/section8-image.png")
    image = imageOpen.openFile()
    count = 0
    task_ids = []
    results = []
    for chunk in image:
        task_ids.append(tasks.imageThresholding.delay(chunk, 127, 255))
        count += 1
    for result in task_ids:
        result = result.get()
        results.append(result)

