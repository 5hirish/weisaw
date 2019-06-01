import os
from dotenv import load_dotenv


def load_env_config(verbose=False):
    load_dotenv(verbose=verbose)
