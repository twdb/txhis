import ConfigParser
from sqlalchemy import create_engine, func, Index
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import and_

from wof.dao import BaseDao

import pyhis_models as model


class PyhisDao(BaseDao):
    contact_info = {
        'name': 'NAME',
        'phone': 'PHONE',
        'email': 'EMAIL',
        'organization': 'ORGANIZATION',
        'link': 'LINK',
        'description': 'DESCRIPTION',
        'address': 'ADDRESS',
        'city': 'CITY',
        'state': 'STATE',
        'zipcode': 'ZIP'
        }

    def __init__(self, db_connection_string, config_file_path):
        self.engine = create_engine(db_connection_string, echo=True,
                                    convert_unicode=True)
        #TODO: Use pool_size for non-sqlite database connection
        self.db_session = scoped_session(sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine))
        self._create_indexes()
        model.init_model(self.db_session)
        config = ConfigParser.RawConfigParser()
        config.read(config_file_path)
        if config.has_section('Contact'):
            self.contact_info = {
                'name': config.get('Contact', 'Name'),
                'phone': config.get('Contact', 'Phone'),
                'email': config.get('Contact', 'Email'),
                'organization': config.get('Contact', 'Organization'),
                'link': config.get('Contact', 'Link'),
                'description': config.get('Contact', 'Description'),
                'address': config.get('Contact', 'Address'),
                'city': config.get('Contact', 'City'),
                'state': config.get('Contact', 'State'),
                'zipcode': config.get('Contact', 'ZipCode')
                }

    def __del__(self):
        self.db_session.close()

    def _create_indexes(self):
        # create an index on timeseries values if it doesn't exist
        try:
            i = Index('ix_timeseries_values_id',
                      model.DataValue.__table__.c.timeseries_id)
            i.create(self.engine)
        except OperationalError:
            pass

    def get_all_sites(self):
        return model.Site.query.all()

    def get_site_by_code(self, site_code):
        return model.Site.query.filter(
            model.Site.SiteCode == site_code).first()

    def get_sites_by_codes(self, site_codes_arr):
        return model.Site.query.filter(
            model.Site.SiteCode.in_(site_codes_arr)).all()

    def get_all_variables(self):
        return model.Variable.query.all()

    def get_variable_by_code(self, var_code):
        return model.Variable.query.filter(
            model.Variable.VariableCode == var_code).first()

    def get_variables_by_codes(self, var_codes_arr):
        return model.Variable.query.filter(model.Variable.VariableCode.in_(
            var_codes_arr)).all()

    def get_series_by_sitecode(self, site_code):
        siteResult = model.Site.query.filter(
            model.Site.SiteCode == site_code).one()
        if siteResult:
            return siteResult.Series
        return None

    def get_series_by_sitecode_and_varcode(self, site_code, var_code):
        siteResult = model.Site.query.filter(
            model.Site.SiteCode == site_code).one()
        varResult = model.Variable.query.filter(
            model.Variable.VariableCode == var_code).one()

        res = self.db_session.query(
                func.count(model.DataValue.DataValue).label('ValueCount'),
                func.min(model.DataValue.DateTimeUTC).label(
                    'BeginDateTimeUTC'),
                func.max(model.DataValue.DateTimeUTC).label('EndDateTimeUTC'),
            ).filter(
                and_(model.DataValue.SiteID == siteResult.SiteID,
                     model.DataValue.VariableID == varResult.VariableID)).one()
        seriesCat = model.Series(
            siteResult, varResult, 3, res.BeginDateTimeUTC,
            res.EndDateTimeUTC, self.get_source_by_id())

        return [seriesCat]

    def get_datavalues(self, site_code, variable_code, begin_date_time=None,
                       end_date_time=None):
        site = self.get_site_by_code(site_code)
        variable = self.get_variable_by_code(variable_code)

        #first find the site and variable
        series = self.db_session.query(model.Series).filter(
            and_(model.Series.Site==site,
                 model.Series.Variable == variable)).one()


        if site and variable:
            if begin_date_time and end_date_time:
                return series.DataValues.filter(
                    and_(
                        model.DataValue.DateTimeUTC >= begin_date_time,
                        model.DataValue.DateTimeUTC <= end_date_time)).order_by(
                    model.DataValue.DateTimeUTC.asc()).all()
            else:
                return series.DataValues.order_by(
                    model.DataValue.DateTimeUTC.asc()).all()

                # return model.DataValue.query.filter(
                #     and_(model.DataValue.SiteID == 1,
                #          model.DataValue.VariableID == 6,
                #          #assume we don't have localdatetime, so using UTC
                #          model.DataValue.DateTimeUTC >= begin_date_time,
                #          model.DataValue.DateTimeUTC <= end_date_time)
                #     ).order_by(model.DataValue.DateTimeUTC).all()

    def get_method_by_id(self, methodID):
        return model.Method.query.filter(
            model.Method.MethodID == methodID).first()

    def get_methods_by_ids(self, method_id_arr):
        return model.Method.query.filter(
            model.Method.MethodID.in_(method_id_arr)).all()

    def get_source_by_id(self, source_id=1):
        source = model.Source()

        source.ContactName = self.contact_info['name']
        source.Phone = self.contact_info['phone']
        source.Email = self.contact_info['email']
        source.Organization = self.contact_info['organization']
        source.SourceLink = self.contact_info['link']
        source.SourceDescription = self.contact_info['description']
        source.Address = self.contact_info['address']
        source.City = self.contact_info['city']
        source.State = self.contact_info['state']
        source.ZipCode = self.contact_info['zipcode']

        return source

    def get_sources_by_ids(self, source_id_arr):
        #Assume there is only ever one Source for now
        return [self.get_source_by_id()]

    def get_qualifier_by_id(self, qualifier_id):
        return model.Qualifier()

    def get_qualifiers_by_ids(self, qualifier_id_arr):
        return [model.Qualifier()]

    def get_qualcontrollvl_by_id(self, qual_control_lvl_id):
        return model.QualityControlLevel()

    def get_qualcontrollvls_by_ids(self, qual_control_lvl_id_arr):
        return [model.QualityControlLevel()]

    def get_offsettype_by_id(self, offset_type_id):
        #TODO
        return None

    def get_offsettypes_by_ids(self, offset_type_id_arr):
        #TODO
        return None
