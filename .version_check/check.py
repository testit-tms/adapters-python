import re
import sys

if len(sys.argv) < 2:
    print("Usage: python check.py <your_parameter>")
    sys.exit(1)


def pipi_is_canonical(version):
    return re.match(r'^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$', version) is not None

def check_version(version):
    print(f"Received version: {param}")
    if not pipi_is_canonical(version):
        raise Exception("Version " + version + " is not canonical for pypi")
    else:
        print("Version OK")
    

param = sys.argv[1]  # First argument after script name
check_version(param)