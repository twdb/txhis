"""
This CBI to WaterML web service accepts WaterML requests and
translates them into OGC SOS (The OpenGIS Sensor Observation Service)
calls to the GCOOS (The Gulf of Mexico Coastal Ocean Observing
System), returning WaterML responses.
"""

from setuptools import setup

setup(
    name='CBI_WaterML_service',
    version='0.2a',
    long_description=__doc__,
    packages=['cbi'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'dateutil',
        'Flask',
        'soaplib',
        'SQLAlchemy',
        'WOFpy']
)
