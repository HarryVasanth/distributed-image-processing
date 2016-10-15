from __future__ import absolute_import

from celery import Celery

#TODO Change the broker for it to be able to use different machines (Virtual ones)
app = Celery('Distributed-Systems-Image-Processing',
             backend='rpc://',
             broker='amqp://guest@localhost//',
             include=['Distributed-Systems-Image-Processing.tasks'])
