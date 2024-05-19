from setuptools import find_packages, setup

setup(
    name='testit-adapter-pytest',
    version='3.2.0',
    description='Pytest adapter for Test IT',
    long_description=open('README.md', "r").read(),
    long_description_content_type="text/markdown",
    url='https://github.com/testit-tms/adapters-python/',
    author='Integration team',
    author_email='integrations@testit.software',
    license='Apache-2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    py_modules=['testit_adapter_pytest'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=['pytest', 'pytest-xdist', 'attrs', 'testit-python-commons==3.2.0'],
    entry_points={'pytest11': ['testit_adapter_pytest = testit_adapter_pytest.plugin']}
)
