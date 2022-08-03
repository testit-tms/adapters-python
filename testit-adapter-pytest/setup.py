from setuptools import setup

setup(
    name='testit-adapter-pytest',
    version='1.1.2',
    description='Pytest adapter for Test IT',
    url='https://pypi.org/project/testit-adapter-pytest/',
    author='Pavel Butuzov',
    author_email='pavel.butuzov@testit.software',
    license='Apache-2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    py_modules=['testit', 'testit_adapter_pytest'],
    packages=['testit_adapter_pytest'],
    package_dir={'testit_adapter_pytest': 'src'},
    install_requires=['pytest', 'pytest-xdist', 'testit-api-client>=1.1,<2'],
    entry_points={'pytest11': ['testit_adapter_pytest = testit_adapter_pytest.plugin']}
)
