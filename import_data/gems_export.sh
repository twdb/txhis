#!/bin/sh

python ./tpwd_to_cache.py
python ./gems_export.py

sqlite3 ./gems_database.db <<!
.headers on
.output tbl_TexasHIS_Vector_TWDB_ODM_Sites.psv
select * from tbl_TexasHIS_Vector_TWDB_ODM_Sites;
!

sqlite3 ./gems_database.db <<!
.headers on
.output tbl_TexasHIS_Vector_TWDB_ODM_Data.psv
select * from tbl_TexasHIS_Vector_TWDB_ODM_Data;
!

