from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='reportronic_hours',
    version='0.1.0',
    description='Automate logging working hours in Reportronic',
    long_description=readme,
    author='Topi Kettunen',
    author_email='topi@topikettunen.com',
    url='https://github.com/topikettunen/reportronic-hours',
    license=license
)
