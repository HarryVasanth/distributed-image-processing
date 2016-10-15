from __future__ import absolute_import

from celery import Celery

app = Celery('Distributed-Systems-Image-Processing',
             backend='rpc://',
             broker='amqp://guest@localhost//',
             include=['Distributed-Systems-Image-Processing.tasks'])
