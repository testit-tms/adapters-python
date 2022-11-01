from setuptools import setup, find_packages

setup(
    name='testit_adapter_robotframework',
    version='1.0.0',
    description='Robot Framework adapter for Test IT',
    long_description=open('README.md', "r").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/testit-tms/adapters-python/',
    author='Dmitriy Kylosov',
    author_email='mail@dkylosov.ru',
    license='Apache-2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    py_modules=['testit_adapter_robotframework', 'TMSLibrary'],
    packages=find_packages(where='src'),
    package_dir={'testit_adapter_robotframework': 'src/testit_adapter_robotframework',
                 'TMSLibrary': 'src/TMSLibrary'},
    install_requires=['attrs', 'robotframework']
)
