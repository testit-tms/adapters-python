# Test IT Python Integrations
The repository contains new versions of adapters for python test frameworks.

Pytest: [![Release
Status](https://img.shields.io/pypi/v/testit-adapter-pytest?style=plastic)](https://pypi.python.org/pypi/testit-adapter-pytest)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-pytest?style=plastic)](https://pypi.python.org/pypi/testit-adapter-pytest)

Behave: [![Release
Status](https://img.shields.io/pypi/v/testit-adapter-behave?style=plastic)](https://pypi.python.org/pypi/testit-adapter-behave)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-behave?style=plastic)](https://pypi.python.org/pypi/testit-adapter-behave)

Nose: [![Release
Status](https://img.shields.io/pypi/v/testit-adapter-nose?style=plastic)](https://pypi.python.org/pypi/testit-adapter-nose)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-nose?style=plastic)](https://pypi.python.org/pypi/testit-adapter-nose)

Robotframework: [![Release
Status](https://img.shields.io/pypi/v/testit-adapter-robotframework?style=plastic)](https://pypi.python.org/pypi/testit-adapter-robotframework)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-robotframework?style=plastic)](https://pypi.python.org/pypi/testit-adapter-robotframework)

Commons: [![Release
Status](https://img.shields.io/pypi/v/testit-python-commons?style=plastic)](https://pypi.python.org/pypi/testit-python-commons)
[![Downloads](https://img.shields.io/pypi/dm/testit-python-commons?style=plastic)](https://pypi.python.org/pypi/testit-python-commons)


## Compatibility

| Test IT | Behave         | Nose           | Pytest         | RobotFramework |
|---------|----------------|----------------|----------------|----------------|
| 3.5     | 2.0            | 2.0            | 2.0            | 2.0            |
| 4.0     | 2.1            | 2.1            | 2.1            | 2.1            |
| 4.5     | 2.5            | 2.5            | 2.5            | 2.5            |
| 4.6     | 2.8            | 2.8            | 2.8            | 2.8            |
| 5.0     | 3.2            | 3.2            | 3.2            | 3.2            |
| 5.2     | 3.3            | 3.3            | 3.3            | 3.3            |
| 5.3     | 3.6.1.post530  | 3.6.1.post530  | 3.6.1.post530  | 3.6.1.post530  |
| 5.4     | 3.6.6.post540  | 3.6.6.post540  | 3.6.6.post540  | 3.6.6.post540  |
| 5.5     | 3.10.1.post550 | 3.10.1.post550 | 3.10.1.post550 | 3.10.1.post550 |
| 5.6     | 3.11.0.post560 | 3.11.0.post560 | 3.11.0.post560 | 3.11.0.post560 |
| Cloud   | 3.10.4 +       | 3.10.4 +       | 3.10.4 +       | 3.10.4 +       |

1. For current versions, see the releases tab. 
2. Starting with 5.2, we have added a TMS postscript, which means that the utility is compatible with a specific enterprise version. 
3. If you are in doubt about which version to use, check with the support staff. support@yoonion.ru

Supported test frameworks:
 1. [Pytest](https://github.com/testit-tms/adapters-python/tree/main/testit-adapter-pytest)
 2. [Behave](https://github.com/testit-tms/adapters-python/tree/main/testit-adapter-behave)
 3. [RobotFramework](https://github.com/testit-tms/adapters-python/tree/main/testit-adapter-robotframework)
 4. [Nose](https://github.com/testit-tms/adapters-python/tree/main/testit-adapter-nose) 

# 🚀 Warning
Since 3.0.0 version:
- If the externalId annotation is not specified, then its contents will be a hash of a fully qualified method name.

<a href='https://coveralls.io/github/testit-tms/adapters-python?branch=main'>
    <img src='https://coveralls.io/repos/github/testit-tms/adapters-python/badge.svg?branch=main' alt='Coverage Status' />
</a>
