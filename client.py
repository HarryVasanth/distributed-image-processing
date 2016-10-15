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

        matrix = genArray(size)
        print("The matrix to convert is: ")
        print(matrix)

        result = applyGauss.delay(matrix,sigma) # Puts a new task in the queue

        print("Matrix after applying gaussian filter:")
        print(result.get()) # Gets the result from the worker

    except Exception as e:
        if type(e) is ValueError:
            print("Please check if you typed a number.")
