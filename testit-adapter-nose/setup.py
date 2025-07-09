from setuptools import setup, find_packages

VERSION = "3.6.5.post530"

setup(
    name='testit-adapter-nose',
    version=VERSION,
    description='Nose adapter for Test IT',
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
    py_modules=['testit_adapter_nose'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['attrs', 'nose2', 'testit-python-commons==' + VERSION],
    entry_points={
            'nose.plugins.0.10': [
                'testit_adapter_nose = testit_adapter_nose.plugin:TmsPlugin',
            ]
    }
)
