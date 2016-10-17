from __future__ import absolute_import

from celery import Celery

app = Celery('Distributed-Systems-Image-Processing',
             broker='amqp://dist:dist@192.168.10.94/imageproc', # The IP should be changed!
             backend='redis://192.168.10.170:6379/0', # The IP should be changed!
             include=['Distributed-Systems-Image-Processing.tasks'])
