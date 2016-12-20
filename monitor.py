from celery import Celery

import csv

def my_monitor(app):
    print("Montoring")
    state = app.events.State()
    print("Waiting.......")
    def announce_success_tasks(event):
        print("Enter Here")
        state.event(event)
        task = state.tasks.get(event['uuid'])

        print("TASK SUCEESS : %s[%s] %s" %(
            task.name,task.uuid,task.timestamp,
        ))


    def announce_failed_tasks(event):
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = state.tasks.get(event['uuid'])

        print('TASK FAILED: %s[%s] %s' % (
            task.name, task.uuid, task.info(),))

    with app.connection() as connection:
        print("Connection Received")
        recv = app.events.Receiver(connection, handlers={
                'task-failed': announce_failed_tasks,
                'task-started': announce_success_tasks,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

class GenerateCSV():
    """
    Generates a csv file with all the data from the tests
    """

    def __init__(self, name):
        with open(name + ".csv", 'a', newline='') as fp:
            self.a = csv.writer(fp, delimiter=',')
            self.a.writerow(
                ['Task', 'Task Received', 'Task Started', 'Task Succeed', 'Queue Time','Time of Processing','Total Time', 'WorkerName'])

    def writeRow(self, taskname,receivedTime, startTime, endTime, whichworker):
        """
        Write a row in the CSV file
        """
        self.a.writerow([taskname, receivedTime, startTime, endTime, receivedTime-startTime, endTime-startTime,endTime - receivedTime, whichworker])



if __name__ == '__main__':
    print("Starting Monitor")
    app = Celery(broker='amqp://dist:dist@192.168.1.8/imageproc')
    my_monitor(app)