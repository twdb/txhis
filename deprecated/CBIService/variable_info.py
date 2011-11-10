#This file serves as a dictionary for all variables available from CBI
variable_Dictionary ={
        #Air temperature
        'atp': {"variableID" :"1",
                           "variableCode": "atp",
                           "variableName":"AirTemperature",
                           "units": { "abbr": "degC",
                                      "unitsCode": 96,
                                      "unitsType": "Temperature",
                                      "name": "degree celcius" 
                                     },
                           "medium": "Air",
                            },
        'bpr': {"variableID" :"2",
                        "variableCode": "bpr",
                        "variableName":"AirPressure",
                        "units": { "abbr": "mbar",
                                    "unitsCode": 90,
                                    "unitsType": "Temperature",
                                    "name": "millibar" 
                                     },
                        "medium": "Air",
                        },
        'pwl': { "variableID" :"5",
                        "variableCode": "pwl",
                        "variableName":"WaterLevel",
                        "units": { "abbr": "m",
                                   "unitsCode": 52,
                                   "unitsType": "Length",
                                   "name": "meter" 
                              },
                        "medium": "Surface Water",
                        },
        'wsd': {"variableID" :"10",
                  "variableCode": "wsd",
                  "variableName":"Winds",
                  "units": { "abbr": "m/s",
                             "unitsCode": 119,
                             "unitsType": "Velocity",
                             "name": "meters per second" 
                            },
                  "medium": "Air",
                },
        'wtp': {"variableID" :"11",
                           "variableCode": "wtp",
                           "variableName":"WaterTemperature",
                           "units": { "abbr": "degC",
                                      "unitsCode": 96,
                                      "unitsType": "Temperature",
                                      "name": "degree celcius" 
                                     },
                           "medium": "Surface Water",
                           },
        'do': {"variableID" :"3",
                            "variableCode": "do",
                            "variableName":"DissolvedOxygen",
                            "units": { "abbr": "mg/L",
                                    "unitsCode": 199,
                                    "name": "milligrams per liter" 
                            },
                            "medium": "Surface Water",
                           },
        'sal': {"variableID" :"7",
                     "variableCode": "sal",
                     "variableName":"Salinity",
                     "units": { "abbr": "psu",
                                "unitsCode": 193,
                                "name": "practical salinity units" 
                              },
                     "medium": "Surface Water",
                    },
        'vlx': {"variableID" :"9",
                     "variableCode": "vlx",
                     "variableName":"Currents",
                     "units": { "abbr": "m/s",
                                "unitsCode": 119,
                                "unitsType": "Velocity",
                                "name": "meters per second" 
                              },
                     "medium": "Surface Water",
                    },
        'rlh':{"variableID" :"6",
                           "variableCode": "rlh",
                           "variableName":"RelativeHumidity",
                           "units": { "abbr": "%",
                                      "unitsCode": 1,
                                      "unitsType": "Dimensionless",
                                      "name": "percent" 
                                     },
                            "medium": "Air",
                           },
        'swh': {"variableID" :"8",
                  "variableCode": "swh",
                  "variableName":"Waves",
                  "units": { "abbr": "m",
                             "unitsCode": 52,
                             "unitsType": "Length",
                             "name": "meter" 
                            },
                  "medium": "Surface Water",
                           },
        'par':{ "variableID" :"4",
                           "variableCode": "par",
                           "variableName":"SolarRadiation",
                           "units": { "abbr": "umol/m2 s",
                                    "unitsCode": 309,
                                    "name": "micromoles per square meter per second" 
                            },
                            "medium": "unknown",      
                      }
        }

#dictionary of name to code mapping
name_to_code_mappingDictionary = dict([[name,code] for code,name 
                                in map(lambda x:(x[0],x[1]["variableName"]),variable_Dictionary.items())])

if __name__ == "__main__":
    print variable_Dictionary
    print name_to_code_mappingDictionary
