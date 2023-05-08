
from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='UR_application',
    version='0.1.0',
    description='Application for remote access to the UR5 CB2 series robots, image proccesing and cooperation of the robot with camera',
    long_description=readme,
    author='Kamil Skop',
    author_email='kamil.skop.tau@gmail.com',
    url='https://github.com/NavierMillennium/UR_Application',
    license=license,
    packages=find_packages(exclude=('src'))
)