import logging
import random
import time

import testit_api_client


def retry(func):
    def retry_wrapper(*args, **kwargs):
        attempts = 0
        retries = 10

        while attempts < retries:
            try:
                return func(*args, **kwargs)
            except testit_api_client.exceptions.ApiException as e:
                sleep_time = random.randrange(0, 100)
                time.sleep(sleep_time/100)
                attempts += 1

                logging.error(e)

    return retry_wrapper
