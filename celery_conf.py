from __future__ import absolute_import

from celery import Celery

#TODO Change the broker for it to be able to use different machines (Virtual ones)
app = Celery('Distributed-Systems-Image-Processing',
             broker='amqp://dist:dist@192.168.10.94/imageproc', # The IP should be changed!
             backend='redis://192.168.10.170:6379/0', # The IP should be changed!
             include=['Distributed-Systems-Image-Processing.tasks'])
