from celery import Celery

app = Celery('Distributed-Image-Processing-System',
             broker='amqp://dist:dist@localhost/imageproc', # The IP shoul$
             backend='redis://localhost:6379/0', # The IP should be change$
             include=['client'])
app.conf.task_serializer = 'pickle'
app.conf.result_serializer = 'pickle'
app.conf.accept_content = ['pickle']
app.conf.worker_send_task_events = 'true'
