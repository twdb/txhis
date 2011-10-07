"""
This service provides TPWD data as WaterML.
"""

from setuptools import setup

setup(
    name='TPWD_WaterML_service',
    version='0.1',
    long_description=__doc__,
    packages=['tpwd'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'soaplib',
        'SQLAlchemy',
        'WOFpy']
)
