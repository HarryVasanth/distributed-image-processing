import os
import cv2  # THis will import open cv 2
from tkinter import *
import tasks
import collections
import numpy as np


class File():
    """
    Implements all file operation Open Close and Save Files
    """

    def __init__(self, path):
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
        self.im = cv2.imread(self.path, cv2.IMREAD_GRAYSCALE)
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

    def saveFile(self, image):
        """
        Write the received matrix to a image file on the directory
        :return:
        """
        dir = "printado.png"
        cv2.imwrite(dir, image)


def checkForNoneResults(results):
    for result in results:
        if not isinstance(result, np.ndarray):
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
            task_ids.append(algorithm.delay(chunk, float(parameters.get("parameter1"))))
        elif len(parameters) == 2:
            task_ids.append(
                algorithm.delay(chunk, float(parameters.get("parameter1")), float(parameters.get("parameter2"))))
        elif len(parameters) == 3:
            task_ids.append(
                algorithm.delay(chunk, float(parameters.get("parameter1")), float(parameters.get("parameter2")),
                                float(parameters.get("parameter3"))))

        results.append(None)
    while checkForNoneResults(results):
        count = 0
        for result in task_ids:
            if result.ready():
                results[count] = result.get()
            count += 1
    results = np.array(results)
    imageOpen.saveFile(results)

def mainMenu():
    """ Function to display Main Menu"""
    ans = True
    while ans:
        print("1. Select spliting algorithm")
        print("2. Define an image folder path")
        print("9.Exit/Quit")
        ans = input("What would you like to do? ")
        if ans == "1":
            par1, par2, function = algorithmsMenu()
            singleImage(function,par1,par2)
        elif ans == "2":
            par1, par2, function = algorithmsMenu()
            multiImage(function, par1, par2)
        elif ans == "9":
            print("\n Goodbye")
            ans = None
        else:
            print("\n Not a valid choice! Please try again...")


def algorithmsMenu():
    """
    Selection Menu - Front End Isolation
    :return:
    """
    ans = True
    while ans:
        print("1. Edge Detection")
        print("2. Thresholding")
        print("3. Rotation")
        print("4. Smooth by Averaging")
        print("5. Laplacian Derivative")
        print("9. Exit/Quit")
        ans = input("What would you like to do? ")
        if ans == "1":
            ans2 = input("Insert minimum value:")
            ans3 = input("Insert maximum value:")
            function = tasks.edgeDetection
            return ans2, ans3, function
        elif ans == "2":
            ans2 = input("Insert threshold value:")
            ans3 = input("Insert maximum value:")
            function = tasks.imageThresholding
            return ans2, ans3, function
        elif ans == "3":
            ans2 = input("Insert angle:")
            ans3 = input("Insert scale:")
            function = tasks.rotation
            return ans2, ans3, function
        elif ans == "4":
            ans2 = input("Insert Kernel's X:")
            ans3 = input("Insert Kernel's Y:")
            function = tasks.smoothBy_Averaging
            return ans2, ans3, function
        elif ans == "5":
            function = tasks.laplacianDerivative
            return None, None, function
        elif ans == "9":
            print("\n Goodbye")
            ans = None
            return None, None, None
        else:
            print("\n Not a valid choice! Please try again...")


def singleImage(function, par1, par2):
    """
    Single image algorithm calls
    :param function:
    :param par1:
    :param par2:
    :return:
    """
    if par1 is None and par2 is None and function is None:
        return
    else:
        imagePath = input("Insert Image Path:")
        algorithmApplier(function, imagePath, False, parameter1=par1, parameter2=par2)

def multiImage(function,par1,par2):
    """
    Multiple image algorithm processing
    :return:
    """
    if par1 is None and par2 is None and function is None:
        return
    else:
        imagePath = input("Insert Image Folder Path:")
        # Making the path an absolute one
        fullPathToImage = os.path.abspath(imagePath)
        try:
            for filename in os.listdir(fullPathToImage):
                if filename.endswith(".png") or filename.endswith(".jpg"):
                    algorithmApplier(function, fullPathToImage + "/" + filename, True, parameter1=par1, parameter2=par2)
                else:
                    print("Can't use this file")
        except FileNotFoundError:
            print("Check if you entered the right path")

    print("The Image Processing has finished")


if __name__ == "__main__":
    mainMenu()
