import math
import os
import time
from datetime import datetime

import pytz

from .P import P


class T:

    def __init__(self):
        self.t = time.time()

    def taken(self, message=None):
        start_time = self.t
        P.yellow("---------------------------------------")
        if message is not None:
            P.yellow("--- " + message + " ---")
        sec = round(time.time() - start_time, 0)
        seconds = int(math.fmod(sec, 60))
        minutes = int(sec // 60)
        time_diff = (time.time() - start_time)
        P.yellow(f"--- {time_diff} seconds --- ")
        P.yellow(f"--- %s minutes %s seconds --- " % (minutes, seconds))
        P.yellow("---------------------------------------")
        return time_diff

    @staticmethod
    def get_london_date_time(date_format=None):
        dt_london = datetime.now(pytz.timezone('Europe/London'))
        return dt_london if date_format is None else dt_london.strftime(date_format)

    @staticmethod
    def get_new_york_date_time(date_format=None):
        tz_ny = pytz.timezone('America/New_York')
        datetime_ny = datetime.now(tz_ny)
        return datetime_ny if date_format is None else datetime_ny.strftime(date_format)

    @staticmethod
    def get_local_date_time(date_format=None):
        local = datetime.now()
        return local if date_format is None else local.strftime(date_format)

    @staticmethod
    def get_file_name(nikgappstype, android_version, arch="arm64"):
        current_time = T.get_current_time()
        return "NikGapps-" + nikgappstype + f"-{arch}-" + str(android_version) + "-" + current_time + ".zip"

    @staticmethod
    def get_current_time():
        tz_london = pytz.timezone('Europe/London')
        datetime_london = datetime.now(tz_london)
        return datetime_london.strftime("%Y%m%d")

    @staticmethod
    def get_path(user_name, android_code):
        tz_london = pytz.timezone('Europe/London')
        datetime_london = datetime.now(tz_london)
        return user_name + "/" + "NikGapps-" + str(android_code) + "/" + str(datetime_london.strftime("%d-%b-%Y"))

    @staticmethod
    def get_mtime(pkg_zip_path):
        return datetime.fromtimestamp(os.path.getmtime(pkg_zip_path))

    @staticmethod
    def format_time(seconds):
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        parts = []
        if days > 0:
            parts.append(f"{days} {'day' if days == 1 else 'days'}")
        if hours > 0:
            parts.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
        if minutes > 0:
            parts.append(f"{minutes} {'minute' if minutes == 1 else 'minutes'}")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} {'second' if seconds == 1 else 'seconds'}")
        return ', '.join(parts)
