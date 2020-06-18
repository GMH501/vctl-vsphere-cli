import sys
import time

try:
    from pyVim.task import WaitForTask
except:
    from pyvim.task import WaitForTask


def progressMeter():
    while True:
        for cursor in '|/-\\':
            yield cursor


spinner = progressMeter()


def taskProgress(task, percentDone):
    """
    """
    sys.stdout.write('\b')
    sys.stdout.write(spinner.__next__())
    sys.stdout.flush()
    time.sleep(0.5)
    sys.stdout.write('\b')
    #  task.info.progress


def waiting(task):
    WaitForTask(task, onProgressUpdate=taskProgress)
    sys.stdout.write('\r ')
