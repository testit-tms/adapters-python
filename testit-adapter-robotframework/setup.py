from setuptools import setup, find_packages

setup(
    name='testit-adapter-robotframework',
    version='2.0.4',
    description='Robot Framework adapter for Test IT',
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
    ],
    py_modules=['testit_adapter_robotframework'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['attrs', 'robotframework', 'testit-python-commons>=2,<3']
)