"""
Module to return formatted date strings.

Depends on: none
"""

import logging
import time

# import libraries
from datetime import datetime


# get date and time
def get_formatted_date_string():
    logging.debug("Called get_formatted_date_string")
    """
    Returns a tuple of the Elite Dangerous Time and the current real world time.

    :rtype: tuple
    """
    posix_time_string = int(time.time())
    logging.debug(f"POSIX time is {posix_time_string}")

    dt_now = datetime.utcnow()

    current_time_string = dt_now.strftime("%Y%m%d_%H%M%S")
    logging.debug(f"Current time string: {current_time_string}")

    return current_time_string, posix_time_string
