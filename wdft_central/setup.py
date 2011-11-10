"""This service provides some helpful information about services
associated with Water Data for Texas, like unit conversion and a
standard way of querying for things like 'salinity', etc.
"""

from setuptools import setup

setup(
    name='wdft_central',
    version='0.1',
    long_description=__doc__,
    packages=['wdft_central'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'soaplib',
        'SQLAlchemy',
        ]
)
