from datetime import datetime


def convert_time(time):
    date = datetime.strptime(time, "%Y%m%d %H:%M:%S.%f")
    date = date.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return date


STATUSES = {'FAIL': 'Failed', 'PASS': 'Passed', 'SKIP': 'Skipped', 'NOT RUN': 'Skipped'}
