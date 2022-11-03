from setuptools import setup, find_packages

setup(
    name='testit-python-commons',
    version='2.0.1',
    description='Python commons for Test IT',
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
        'Programming Language :: Python :: 3.10'
    ],
    py_modules=['testit', 'testit_python_commons'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['pluggy', 'testit-api-client>=2,<3']
)
