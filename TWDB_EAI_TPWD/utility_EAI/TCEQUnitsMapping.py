#Units mapping for TCEQ. key: TCEQ unit code, value: UnitsID in ODM database
unitsMap = {
            #length
            'FT': 48,'IN':49,'MM':54,'M':52,'MI':53,'MI2':58,'KM':51,'CM':47,
            #Area:
            'KM2':16, 'M2':17,'FT2':15, 
            #Time:
            'HOURS':103, 'DAYS':104, 'MIN':102, 'SEC':100, 
            #angle
            'DEG':2,
            #volume
            'AC-FT':123,'L':128,
            #velocity
            'FT/SEC':113,
            #flow
            'GAL/DAY':145, 'CFS':35, 'M3/SEC':288, 'TONS/DAY':145, 
            #turbidity
            'JTU':281, 'NS':224,'NTU':221, 'MGD':40,
            #salinity
            'PPT':306, 
            #temperature
            'DEG C':96, 'DEG F':97,
            #disolved oxygen
            'MG/L':199, '% SAT':308,
            #concentration
            'MG/KG':312, 'G/M2':313, 'G/KG':314,'UG/KG':315, 'UG/L':204,'MG/G':316,'NG/KG':317,
            'PG/L':328,  'NG/L':217,  'NG/G':318, 'UG/CM2':319, 'UG/G':320, 'MMOL/KG':214, 'MG/CM2':321, 
            #organism concentration
            'PCI/L':235, 'PCI/G':324, '#/100ML':239, 'MPN/100ml':249, '#/M2':234, '#/ML':326,
            'CELLS/ML':237, '#/L':235, '#/FT2':327,
            #mass
            'G':65, 'LB':69,'% DRY WT':1,
            #potential difference
            'mV':169,
            #electricity conductivity
            'uS/cm':192, 
            #mass per day
           
            #number, map to dimensionless, count number
            #nu: count,
            #PCU: platium cobalt unit,
            #S.U: ph
            'NU':257,'PCU':231, 'S.U.':309, '%':1, '% FS':1,'% BY WT':1,'#IND':257,'#/SAMP':325,
            '#COLLECTED':257,    
            
            #scale:
            'M/KM':322, #to change to 323
            'FT/FT':323  
            }

mediaMapping = {
            'Water':'Surface Water', 'Air':'Air', 'Sediment':'Sediment',
            'Biological Tissue':'Tissue','Soil':'Soil','Other':'Other'}


if __name__ == "__main__":
    print "# of different units:", len(unitsMap.keys())