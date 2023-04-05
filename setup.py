"""setup.py file."""

from setuptools import setup, find_packages

__author__ = 'Jens Vogler <vogler@init7.net>'

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

setup(
    name="napalm-slx_os",
    version="0.1.0",
    packages=find_packages(),
    author="Jens Vogler",
    author_email="vogler@init7.net",
    description="SLX-OS Driver for NAPALM",
    classifiers=[
        'Topic :: Utilities',
         'Programming Language :: Python',
         'Programming Language :: Python :: 2',
         'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/napalm-automation/napalm-slx_os",
    include_package_data=True,
    install_requires=reqs,
)
