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

""" Function to reuse in algorithm application"""
def algorithmApplier(algorithm, path, **parameters):
    imageOpen = File(path)
    image = imageOpen.openFile()
    
    task_ids = []
    results = []

    print(parameters)
    for chunk in image:
        if len(parameters) == 0:
            task_ids.append(algorithm.delay(chunk))
        elif len(parameters) == 1:
            task_ids.append(algorithm.delay(chunk,parameters.get("parameter1")))
        elif len(parameters) == 2:
            task_ids.append(algorithm.delay(chunk,float(parameters.get("parameter1")),float(parameters.get("parameter2"))))
        elif len(parameters) == 3:
            task_ids.append(algorithm.delay(chunk,parameters.get("parameter1"),parameters.get("parameter2"),parameters.get("parameter3")))
            
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
        print("1. Edge Detection")
        print("2. Thresholding")
        print("3. Rotation")
        print("4. Smooth by Averaging")
        print("5. Laplacian Derivative")
        print("9. Exit/Quit")
        ans=input("What would you like to do? ")
        if ans=="1":
            handleEdgeDetection()
        elif ans=="2":
            handleImageThresholding()
        elif ans=="3":
            handleRotation()
        elif ans=="4":
            handleSmoothAveraging()
        elif ans=="5":
            handleLaplacianDerivative()
        elif ans=="9":
          print("\n Goodbye") 
          ans = None
        else:
           print("\n Not a valid choice! Please try again...")

def mainMenu():
    """ Function to display Main Menu"""
    ans=True
    while ans:
        print("1. Select spliting algorithm")
        print("2. Define an image folder path")
        print("3.")
        print("4.")
        print("5.")
        print("9.Exit/Quit")
        ans=input("What would you like to do? ")
        if ans=="1":
            algorithmsMenu()
        elif ans=="2":
            imageFolderPath()
        elif ans=="9":
          print("\n Goodbye") 
          ans = None
        else:
           print("\n Not a valid choice! Please try again...")

def handleEdgeDetection():
     ans=input("Insert Image Path:")
     image = ans;

     ans2 = input("Insert minimum value:")
     minVal = ans2;

     ans3 = input("Insert maximum value:")
     maxVal = ans3;

     algorithmApplier(tasks.edgeDetection, image, parameter1=minVal, parameter2 = maxVal);
     

     

def handleImageThresholding():
     ans=input("Insert Image Path:")
     image = ans

     ans2 = input("Insert threshold value:")
     thresholdValue = ans2

     ans3 = input("Insert maximum value:")
     maxVal = ans3

     print(image)
     print(thresholdValue)
     print(maxVal)
     algorithmApplier(tasks.imageThresholding, image, parameter1=thresholdValue, parameter2 = maxVal);
     

def handleRotation():
     ans=input("Insert Image Path:")
     image = ans;

     ans2 = input("Insert angle:")
     angle = ans2;

     ans3 = input("Insert scale:")
     scale = ans3;

     algorithmApplier(tasks.rotation, image, parameter1=angle, parameter2 = scale);
     
     

def handleSmoothAveraging():
     ans=input("Insert Image Path:")
     image = ans;

     ans2 = input("Insert Kernel's X:")
     kernelX = ans2;

     ans3 = input("Insert Kernel's Y:")
     kernelY = ans3;

     algorithmApplier(tasks.smoothBy_Averaging, image, parameter1=kernelX, parameter2 = kernelY);
     

def handleLaplacianDerivative():
    ans=input("Insert Image Path:")
    image = ans

    algorithmApplier(tasks.laplacianDerivative, image);
     

def imageFolderPath():
     ans=input("Insert Image Folder Path:")
     image = ans;

if __name__ == "__main__":
    '''imageOpen = File("./images/section8-image.png")
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
    imageOpen.saveFile(results)'''
    mainMenu()
