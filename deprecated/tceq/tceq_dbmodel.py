# ftp://ftp.tceq.state.tx.us/pub/WaterResourceManagement/WaterQuality/DataCollection/CleanRivers/public/stnsmeta.txt
class Site(Object):
    def __init__(self,):
        basin_id
        tceq_station_id
        usgs_guage_id
        short_description
        long_description
        stream_station_location_type
        stream_station_condition_type
        county
        tceq_county_id
        stream_segment
        tceq_region
        latitude
        longitude
        nhd_reach
        on_segment

# http://www.tceq.texas.gov/assets/public/compliance/monops/crp/data/ParameterCodeFieldDescriptions.pdf
class Parameter():
    parameter_code
    description
    units
    media
    method

# http://www.tceq.state.tx.us/assets/public/compliance/monops/crp/data/event_struct.pdf
class Event():
    tag_id
    station_id #fk to site
    end_date
    end_time
    end_depth
    start_date
    start_time
    start_depth
    category # T=time, S=space, B=both, and F=flow weight
    number_of_samples #called type ##/CN/GB
    comment
    submitting_entity #fk to Chapter 4 of the Data Management Reference Guide
    collecting_entity #fk to Chapter 4 of the Data Management Reference Guide
    monitoring_type #fk TCEQ assigns valid codes, and they are listed in Chapter 4 of the Data Management Reference Guide (e.g., RT=Routine ambient sampling, BF=Sampling biased to high or low flow).

class Result():
    tag_id #fk to Event
    end_date #must match event end_data
    parameter_code
    gtlt #value > or < quantification limits or blank
    value
    lod #limit of Detection
    loq #Limit of Quantification
    qualifier_code # from chapter 9 of reference
    verify_flag #if value outside max/min limits & TCEQ verifies as correct then = 1
