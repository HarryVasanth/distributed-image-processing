import cv2 #THis will import open cv 2
from tkinter import *
import tasks
import collections
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
        dir="printado.png"
        cv2.imwrite(dir,image)

def checkForNoneResults(results):
    for result in results:
        if not isinstance(result,np.ndarray):
            return True
    return False

if __name__ == "__main__":
    imageOpen = File("./images/section8-image.png")
    image = imageOpen.openFile()
    task_ids = []
    results = []
    for chunk in image:
        task_ids.append(tasks.imageThresholding.delay(chunk, 127, 255))
        results.append(None)
    while checkForNoneResults(results):
        count = 0
        for result in task_ids:
            if result.ready():
                results[count] = result.get()
            count += 1
    results = np.array(results)
    imageOpen.saveFile(results)

def algorithmsMenu():
    """Function to display all available algorithms"""
    ans=True
    while ans:
        print(
        1. Edge Detection
        2. Thresholding
        3. Rotation
        4. Smooth by Averaging
        5. Laplacian Derivative
        9. Exit/Quit
        )
        ans=raw_input("What would you like to do? ")
        if ans=="1":
          """Request params ? """
        elif ans=="2":
          """Request params ? """
        elif ans=="3":
          """Request params ? """
        elif ans=="4":
          """Request params ? """
        elif ans=="5":
          """Request params ? """
        elif ans=="9":
          print("\n Goodbye") 
          ans = None
        else:
           print("\n Not a valid choice! Please try again...")

def mainMenu():
    """ Function to display Main Menu"""
    ans=True
    while ans:
        print(
        1. Select spliting algorithm
        2. Define an image folder path
        3. 
        4. 
        5. 
        9.Exit/Quit
        )
        ans=raw_input("What would you like to do? ")
        if ans=="1":
          """Execute algorithmsMenu ?   """
        elif ans=="2":
          """Request folder path? """
       
        elif ans=="9":
          print("\n Goodbye") 
          ans = None
        else:
           print("\n Not a valid choice! Please try again...")


