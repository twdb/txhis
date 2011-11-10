'''
Created on Oct 7, 2010

Database model for TXHIS backend database

@author: CTtan
'''
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy import (Sequence, Integer, Enum, String, Text, Boolean,
                        DateTime, Float)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.interfaces import PropComparator
from sqlalchemy.ext.declarative import declarative_base

import datetime

__all__ = ['Setting', 'User', 'Sources', 'VariableMapping', 'Variables',
           'Units', 'UnitConversionFormula']

Base = declarative_base()
metadata = Base.metadata


# this is for settings info
class Setting(Base):
    __tablename__ = 'setting'

    pk = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    link = Column(String(200), unique=True, nullable=False)
    description = Column(Text)

    theme = Column(String(50), nullable=False)
    google_cse = Column(String(40))
    google_analytics = Column(String(20))
    akismet_key = Column(String(20))
    twitter_id = Column(String(100))

    about = Column(Text)

    ext1 = Column(String(200)) # for future use
    ext2 = Column(String(200)) # for future use
    ext3 = Column(Text) # for future use

    def __init__(self, name="", link="", theme="", description=None):
        self.name = name
        self.link = link
        self.theme = theme
        self.description = description

    def __repr__(self):
        return "<Setting>"


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    fullname = Column(String)
    password = Column(String)
    email = Column(String)
    last_login = Column(DateTime, default=datetime.datetime.now)


class Sources(Base):
    __tablename__ = "Sources"
    __table_args__ = (
        UniqueConstraint('SourceID', 'NetworkName', 'WSDLLink', name='uix_2'),
        {},
        )

    SourceID = Column(Integer, Sequence('source_seq_id', optional=True),
                      primary_key=True)
    NetworkName = Column(String(50), nullable=False)
    SourceSummerizedDescription = Column(String(100), nullable=False)
    SourceDetailedDescription = Column(Text(), nullable=False)
    LogoLink = Column('LogoLink', String(100), nullable=False)
    DescriptionLink = Column(String(100), nullable=False)
    SourceLink = Column(String(100), nullable=False)
    WSDLLink = Column(String(100), nullable=False)
    SourceFormat = Column(String(30), nullable=False)
    UpdateFrequencyType = Column(Enum('Daily', 'Weekly', 'Monthly', 'Ad-Hoc'),
                                 nullable=False)
    UpdateFrequencyValue = Column(String(30), nullable=False)
    LastUpdatedOn = Column(DateTime)
    ContactName = Column(String(20))
    Phone = Column(String(12))
    Email = Column(String(20))
    Address = Column(String(30))
    City = Column(String(30))
    State = Column(String(30))
    ZipCode = Column(String(30))
    Citation = Column(String(30))
    MetadataID = Column(Integer)

    availableParameterInfo = relationship(
        'VariableMapping',
        primaryjoin="VariableMapping.source_id==Sources.SourceID",
        )

    def __repr__(self):
        return self.NetworkName


class VariableMapping(Base):
    __tablename__ = "VariableMapping"
    __table_args__ = (
        UniqueConstraint('source_id', 'RemoteVariableCode', 'RemoteUnitsID',
                         name='uix_1'),
        {},
        )

    MappingID = Column(Integer, Sequence('VarMapping_seq_id', optional=True),
                       primary_key=True)
    source_id = Column(Integer, ForeignKey('Sources.SourceID'))
    variable_id = Column(Integer, ForeignKey('Variables.VariableID'))
    RemoteVariableCode = Column(String(50), nullable=False)
    RemoteUnitsID = Column(Integer, ForeignKey('Units.UnitsID'))

    SourceInfo = relationship(
        'Sources',
        primaryjoin="VariableMapping.source_id == Sources.SourceID")
    STDcentralVariableInfo = relationship(
        'Variables',
        primaryjoin="VariableMapping.variable_id == Variables.VariableID")


class Variables(Base):
    __tablename__ = "Variables"

    VariableID = Column(Integer, Sequence('paramList_seq_id', optional=True),
                        primary_key=True)
    VariableCode = Column(String(50), nullable=False, unique=True)
    VariableName = Column(String(255), nullable=False, unique=True)
    Speciation = Column(String(255))
    VariableUnitsID = Column(Integer, ForeignKey('Units.UnitsID'))
    SampleMedium = Column(String(255))
    ValueType = Column(String(255))
    IsRegular = Column(Boolean)
    TimeSupport = Column(Float)
    TimeUnitsID = Column(Integer)
    DataType = Column(String(255))
    GeneralCategory = Column(String(255))
    NoDataValue = Column(Float)

    UnitInfo = relationship(
        'Units',
        primaryjoin="Units.UnitsID == Variables.VariableUnitsID")

    def __repr__(self):
        return self.VariableName


class Units(Base):
    __tablename__ = "Units"

    UnitsID = Column(Integer, Sequence('Units_seq_id', optional=True),
                     primary_key=True)
    UnitsName = Column(String(255), nullable=False, unique=True)
    UnitsType = Column(String(255), nullable=False)
    UnitsAbbreviation = Column(String(255), nullable=False)

    def __repr__(self):
        return self.UnitsName


class UnitConversionFormula(Base):
    __tablename__ = "UnitConversionFormula"
    __table_args__ = (
        UniqueConstraint("SourceUnitsID", "DestinationUnitsID",
                         name="MappingPair"),
        {},
        )

    FormulaID = Column(Integer, Sequence('Formula_seq_id', optional=True),
                       primary_key=True)
    SourceUnitsID = Column(Integer, ForeignKey('Units.UnitsID'),
                           nullable=False)
    DestinationUnitsID = Column(Integer, ForeignKey('Units.UnitsID'),
                                nullable=False)
    ConversionFormula = Column(String(50), nullable=False)

    Source_Unit = relationship(
        'Units',
        primaryjoin="Units.UnitsID == UnitConversionFormula.SourceUnitsID")

    Destination_Unit = relationship(
        'Units',
        primaryjoin="Units.UnitsID == UnitConversionFormula.DestinationUnitsID")


#sessions for storing cookie
class Session(Base):
    __tablename__ = 'session'

    session_id = Column(String(128), unique=True, primary_key=True)
    atime = Column(DateTime)
    data = Column(Text)
