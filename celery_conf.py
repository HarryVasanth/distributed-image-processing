from celery import Celery

app = Celery('Distributed-Image-Processing-System',
             broker='amqp://dist:dist@192.168.1.100/imageproc', # The IP shoul$
             backend='redis://192.168.1.100:6379/0', # The IP should be change$
             include=['client'])
app.conf.task_serializer = 'pickle'
app.conf.result_serializer = 'pickle'