"""
export twdb data to gems format
"""
import pyhis

CACHE_DATABASE_FILE = "twdb_pyhis_cache.db"
CACHE_DATABASE_URI = 'sqlite:///' + CACHE_DATABASE_FILE
ECHO_SQLALCHEMY = False
TWDB_WSDL_URL = 'http://his.crwr.utexas.edu/TWDB_Sondes/cuahsi_1_0.asmx?WSDL'

if __name__ == '__main__':
    pyhis.cache.init_cache(CACHE_DATABASE_FILE, ECHO_SQLALCHEMY)
    pyhis.cache.cache_all(TWDB_WSDL_URL)
