from setuptools import find_packages, setup

VERSION = "3.7.1"

setup(
    name='testit-adapter-behave',
    version=VERSION,
    description='Behave adapter for Test IT',
    long_description=open('README.md', "r").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/testit-tms/adapters-python/',
    author='Integration team',
    author_email='integrations@testit.software',
    license='Apache-2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    py_modules=['testit_adapter_behave'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'behave',
        'testit-python-commons==' + VERSION,
        'attrs'],
)
