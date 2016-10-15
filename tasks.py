from scipy.ndimage.filters import gaussian_filter

from celery_conf import app

@app.task
def applyGauss(matrix, sigma):
    '''
    Applies the Gaussin filter in a given matrix with a given sigma
    '''
    return gaussian_filter(matrix, sigma)

