import os
from weisaw.worker.core import celery_task
from dotenv import load_dotenv

if __name__ == '__main__':

    argv = [
        'worker',
        '--loglevel=DEBUG',
    ]
    celery_task.worker_main(argv)
