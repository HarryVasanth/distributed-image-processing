import os
import cv2  # THis will import open cv 2
from tkinter import *
import tasks
import collections
import numpy as np
import time
import csv
import requests
import datetime

class File():
    """
    Implements all file operation Open Close and Save Files
    """

    def __init__(self, path):
        self.path = path

    def openFile(self, loadType):
        """
        This method will open the image
        The path for the image comes when a new object is constructed.
        THere is a few image open modes:
           -1 = cv2.IMREAD_COLOR : Loads a color image. Any transparency of image will be neglected. It is the default flag.
            0 = cv2.IMREAD_GRAYSCALE : Loads image in grayscale mode
            1 = cv2.IMREAD_UNCHANGED : Loads image as such including alpha channel
        """
        self.im = cv2.imread(self.path, loadType)
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

    def saveFile(self, image, dir):
        """
        Write the received matrix to a image file on the directory
        :return:
        """
        print(dir)
        path = os.path.split(dir)[0]
        print(path)
        fileName = os.path.splitext(os.path.split(dir)[1])[0]
        print(fileName)
        extension = os.path.splitext(dir)[1]
        print(extension)
        dir = path + "/results/" + fileName + "_processed" + extension
        print(dir)
        cv2.imwrite(dir, image)


class Handler:
    task_ids = {}
    results = {}
    filename = None
    testNumber = 0
    def restartData(self):
        self.task_ids = {}
        self.results = {}

    def checkForNoneResults(self, results):
        for key, result in results.items():
            if not isinstance(result, np.ndarray):
                return True
        return False

    def splitAndSend(self, image, path, algorithm, parameters):
        count = 0
        for chunk in image:
            if len(parameters) == 0:
                self.task_ids[count] = algorithm.delay(chunk)
            elif len(parameters) == 1:
                self.task_ids[count] = algorithm.delay(chunk, float(parameters.get("parameter1")))
            elif len(parameters) == 2:
                self.task_ids[count] = \
                    algorithm.delay(chunk, float(parameters.get("parameter1")), float(parameters.get("parameter2")))
            elif len(parameters) == 3:
                self.task_ids[count] = \
                    algorithm.delay(chunk, float(parameters.get("parameter1")), float(parameters.get("parameter2")),
                                    float(parameters.get("parameter3")))
            self.results[count] = None
            count = count + 1

    def applyToCompleteImage(self, image, path, algorithm, parameters):
        if len(parameters) == 0:
            self.task_ids[path] = algorithm.delay(image)
        elif len(parameters) == 1:
            self.task_ids[path] = algorithm.delay(image, float(parameters.get("parameter1")))
        elif len(parameters) == 2:
            self.task_ids[path] = \
                algorithm.delay(image, float(parameters.get("parameter1")), float(parameters.get("parameter2")))
        elif len(parameters) == 3:
            self.task_ids[path] = \
                algorithm.delay(image, float(parameters.get("parameter1")), float(parameters.get("parameter2")),
                                float(parameters.get("parameter3")))
        self.results[path] = None

    def checkProcessingState(self):
        self.filename = self.filename + "_"+str(self.testNumber)
        self.testNumber+=1
        newCSV = GenerateCSV(self.filename)
        newCSV.openCSVFile(self.filename)
        while self.checkForNoneResults(self.results):
            for key, result in self.task_ids.items():
                if result.ready():

                    r = requests.get("http://localhost:5555/api/task/info/" + result.id)
                    print("http://localhost:5555/api/task/info/" + result.id)
                    #Parsing Data
                    jsonFile = r.json()
                    print(jsonFile)
                    print(jsonFile['received'])
                    print(jsonFile['started'])
                    print(jsonFile['succeeded'])
                    newCSV.writeRow(self.filename,jsonFile['name'],jsonFile['received'],jsonFile['started'],jsonFile['succeeded'],jsonFile['worker'])
                    self.results[key] = result.get()

    def getSplitResults(self, imageOpen, path):
        self.checkProcessingState()
        self.results = np.array([value for (key, value) in sorted(self.results.items())])
        imageOpen.saveFile(self.results, path)

    def getFolderResults(self, imageOpen):
        self.checkProcessingState()
        for key, result in self.results.items():
            result = np.array(result)
            imageOpen.saveFile(result, key)

    """ Function to reuse in algorithm application"""

    def algorithmApplier(self, algorithm, path, folder, loadType=0, **parameters):
        self.filename = algorithm.__name__
        imageOpen = File(path)
        image = imageOpen.openFile(loadType)

        if (folder):
            self.filename = self.filename + "_allImage"
            self.applyToCompleteImage(image, path, algorithm, parameters)
        else:
            self.filename = self.filename + "_splited"
            self.splitAndSend(image, path, algorithm, parameters)
            self.getSplitResults(imageOpen, path)


def mainMenu():
    """ Function to display Main Menu"""
    ans = True
    while ans:
        print("1. Select spliting algorithm")
        print("2. Define an image folder path")
        print("9.Exit/Quit")
        ans = input("What would you like to do? ")
        if ans == "1":
            imageType = 0
            par1, par2, function, loadType, times = algorithmsMenu(imageType)
            singleImage(function, par1, par2, loadType, times)
        elif ans == "2":
            imageType = 1
            par1, par2, function, loadType, times = algorithmsMenu(imageType)
            multiImage(function, par1, par2, loadType, times)
        elif ans == "9":
            print("\n Goodbye")
            ans = None
        else:
            print("\n Not a valid choice! Please try again...")


def algorithmsMenu(imageType):
    """
    Selection Menu - Front End Isolation
    :return:
    """
    ans = True
    while ans:
        if imageType == 0:
            # SINGLE IMAGE
            print("1. Edge Detection")
            print("2. Thresholding")
            print("3. Smooth by Averaging")
            print("4. Laplacian Derivative")
            print("9. Exit/Quit")
            ans = input("What would you like to do? ")
            if ans == "1":
                ans2 = input("Insert minimum value:")
                ans3 = input("Insert maximum value:")
                ans4 = int(input("Insert number of tests:"))
                function = tasks.edgeDetection
                return ans2, ans3, function, 0, ans4
            elif ans == "2":
                ans2 = input("Insert threshold value:")
                ans3 = input("Insert maximum value:")
                ans4 = int(input("Insert number of tests:"))
                function = tasks.imageThresholding
                return ans2, ans3, function, 0, ans4
            elif ans == "3":
                ans2 = input("Insert Kernel's X:")
                ans3 = input("Insert Kernel's Y:")
                ans4 = int(input("Insert number of tests:"))
                function = tasks.smoothBy_Averaging
                return ans2, ans3, function, -1, ans4
            elif ans == "4":
                ans1 = int(input("Insert number of tests:"))
                function = tasks.laplacianDerivative
                return None, None, function, 0, ans1
            elif ans == "9":
                print("\n Goodbye")
                ans = None
                return None, None, None
            else:
                print("\n Not a valid choice! Please try again...")
        elif imageType == 1:
            # MULTIPLE IMAGES
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
                ans4 = int(input("Insert number of tests:"))
                function = tasks.edgeDetection
                return ans2, ans3, function, 0, ans4
            elif ans == "2":
                ans2 = input("Insert threshold value:")
                ans3 = input("Insert maximum value:")
                ans4 = int(input("Insert number of tests:"))
                function = tasks.imageThresholding
                return ans2, ans3, function, 0, ans4
            elif ans == "3":
                ans2 = input("Insert angle:")
                ans3 = input("Insert scale:")
                ans4 = int(input("Insert number of tests:"))
                function = tasks.rotation
                return ans2, ans3, function, 0, ans4
            elif ans == "4":
                ans2 = input("Insert Kernel's X:")
                ans3 = input("Insert Kernel's Y:")
                ans4 = int(input("Insert number of tests:"))
                function = tasks.smoothBy_Averaging
                return ans2, ans3, function, -1, ans4
            elif ans == "5":
                ans1 = int(input("Insert number of tests:"))
                function = tasks.laplacianDerivative
                return None, None, function, 0, ans1
            elif ans == "9":
                print("\n Goodbye")
                ans = None
                return None, None, None
            else:
                print("\n Not a valid choice! Please try again...")


def singleImage(function, par1, par2, loadType, times):
    """
    Single image algorithm calls
    :param function:
    :param par1:
    :param par2:
    :return:
    """
    if par1 is None and par2 is None and function is None:
        return
    elif par1 is None and par2 is None and function is not None:
        imagePath = input("Insert Image Path:")
        handler = Handler()
        for i in range(times):
            handler.algorithmApplier(function, imagePath, False, loadType)
            handler.restartData()
    else:
        imagePath = input("Insert Image Path:")
        handler = Handler()
        for i in range(times):
            handler.algorithmApplier(function, imagePath, False, loadType, parameter1=par1, parameter2=par2)
            handler.restartData()


def multiImage(function, par1, par2, loadType, times):
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
            time_elapsed = []
            handler = Handler()
            for i in range(times):
                # begin_time = time.time()
                aFile = None
                for filename in os.listdir(fullPathToImage):
                    if filename.endswith(".png") or filename.endswith(".jpg"):
                        if par1 is None and par2 is None and function is not None:
                            handler.algorithmApplier(function, fullPathToImage + "/" + filename, True, loadType)
                        else:
                            handler.algorithmApplier(function, fullPathToImage + "/" + filename, True, loadType,
                                                     parameter1=par1, parameter2=par2)
                        aFile = fullPathToImage + "/" + filename
                    else:
                        print("Can't use this file")
                image = File(aFile)
                handler.getFolderResults(image)
                handler.restartData()
        except FileNotFoundError:
            print("Check if you entered the right path")

    print("The Image Processing has finished")

class GenerateCSV():
    """
    Generates a csv file with all the data from the tests
    """

    def __init__(self, filename):
        """
        Creates the csv and writes the header (Preparing File)
        :param name:
        """
        with open("./csvFile/" + filename + ".csv", 'a', newline='') as fp:
            self.timeConversion = timeCls()
            self.a = csv.writer(fp, delimiter=',')
            self.a.writerow(
                ['Task', 'Task Received', 'Task Started', 'Task Succeed', 'Time Between Reception And Start Processing (s)','Processing Time (s)','Total Time(s)', 'WorkerName'])

    def openCSVFile(self,filename):
        """
        Opens a File in append Mode
        :param filename:
        :return:
        """
        self.a = csv.writer(open("./csvFile/" + filename + ".csv", 'a'))


    def writeRow(self, filename,taskname,receivedTime, startTime, endTime, whichworker):
        """
        Write a row in the CSV file
        """

        self.a.writerow([taskname, self.timeConversion.convertTimeStamp(receivedTime), self.timeConversion.convertTimeStamp(startTime), self.timeConversion.convertTimeStamp(endTime)
                            , startTime-receivedTime, endTime-startTime,endTime - receivedTime, whichworker])
class timeCls():
    """
    Time conversion class
    """
    def convertTimeStamp(self,timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    mainMenu()
