import numpy as np
from tasks import applyGauss

def genArray(size):
    '''
    Generates a random square matrix
    '''
    return np.random.randint(255, size=(size, size))

if __name__ == '__main__':

    try:
        size = int(input("Please enter the size for the matrix: "))
        sigma = float(input("Please enter a sigma value: "))

        result = []

        for i in range(6):  # applies the gaussian filter 6 times
            matrix = genArray(size)
            print("The matrix {0} to convert is: ".format(i))
            print(matrix)

            result.append(applyGauss.delay(matrix,sigma)) # Puts a new task in the queue

        for i in range(6):  # applies the gaussian filter 6 times
            print("Matrix {0} after applying gaussian filter:".format(i))
            print(result[i].get()) # Gets the result from the worker

    except Exception as e:
        if type(e) is ValueError:
            print("Please check if you typed a number.")
