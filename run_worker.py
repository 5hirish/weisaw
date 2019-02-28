import os
from weisaw.worker.core import celery_task

if __name__ == '__main__':

    argv = [
        'worker',
        '-Q weisaw',
        '--loglevel=DEBUG',
    ]
    celery_task.worker_main(argv)
