import logging
import os
from slack_log_handler import SlackLogHandler


def get_logger(name):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)

    log_dir = "/var/log/wahkhen_app/"
    # create file handler which logs even debug messages
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    slack_hook_url = os.getenv("SLACK_HOOK_URL")
    slack_log_channel = os.getenv("SLACK_CHANNEL_NAME")

    # Create slack handler
    sh = SlackLogHandler(slack_hook_url,
                         channel=slack_log_channel, username="celery_worker")

    fh = logging.FileHandler(log_dir+'wahkhen_app.log')
    # fh = logging.FileHandler('epfo_scrapper.log')

    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    sh.setLevel(logging.WARNING)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.addHandler(sh)

    return logger
