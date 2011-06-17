#!/bin/sh

python ./tpwd_to_cache.py
python ./tceq_to_cache.py
python ./twdb_to_cache.py
python ./cache_to_gems.py

# first, we need to delete sites that don't have any data
sqlite3 ./gems_database/gems_database.db <<!
delete from tbl_TexasHIS_Vector_TWDB_ODM_Sites WHERE ODM_SQL_SiteID not in (select distinct ODM_SQL_SiteID from tbl_TexasHIS_Vector_TWDB_ODM_Data);
.headers on
.output ./gems_database/tbl_TexasHIS_Vector_TWDB_ODM_Sites.psv
select * from tbl_TexasHIS_Vector_TWDB_ODM_Sites;
!

sqlite3 ./gems_database/gems_database.db <<!
.headers on
.output ./gems_database/tbl_TexasHIS_Vector_TWDB_ODM_Data.psv
select * from tbl_TexasHIS_Vector_TWDB_ODM_Data;
!

