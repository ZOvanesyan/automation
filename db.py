#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2 
import pandas as pd
import subprocess
from sqlalchemy import create_engine  

if __name__ == "__main__":

    with open ('input_data/orb_branches.csv', 'rb') as infile: 
        data_branch = infile.readlines()
    with open ('input_data/orb_branches2.csv', 'wb') as outfile:
        outfile.writelines(data_branch[2:])

    with open ('input_data/orb_companies.csv', 'rb') as infile: 
        data_company = infile.readlines()
    with open ('input_data/orb_companies2.csv', 'wb') as outfile:
        outfile.writelines(data_company[2:])

#    branches = pd.read_csv('input_data/orb_branches2.csv')
#    companies = pd.read_csv('input_data/orb_companies2.csv')


    conn = psycopg2.connect(
        host='localhost', 
        port=54320, 
        dbname='postgres',
        user='postgres',
    )

    cur = conn.cursor()

    engine = create_engine('postgresql://postgres@localhost:54320/postgres')

#    branches.to_sql('export_branches', engine)
#    companies.to_sql('export_companies', engine)


    cur.execute("CREATE TYPE naics_type AS (naics_code TEXT, naics_description TEXT);")
    conn.commit()

    cur.execute("CREATE TYPE category_type AS (name TEXT, weight REAL);")
    conn.commit()

    cur.execute("CREATE TABLE companies (company_id bigint PRIMARY KEY, parent_company_id bigint, name character varying(255), other_names character varying(255)[], website character varying(1000), city character varying(255), state character varying(255), zip character varying(255), country character varying(255), naics_code character varying(255),  naics_description character varying(255), other_naics_codes naics_type[],  categories category_type[]);") 
    conn.commit()

    cur.execute("CREATE TABLE branches (company_id bigint, branch_id bigint PRIMARY KEY, name character varying(255), other_names character varying(255)[], city character varying(255), state character varying(255), zip character varying(255), country character varying(255));")
    conn.commit()

    cur.execute("CREATE TABLE export_companies AS SELECT * FROM companies;")
    conn.commit()

    cur.execute("CREATE TABLE export_branches AS SELECT * FROM branches;")
    conn.commit()

    cur.execute("COPY export_companies FROM '/var/lib/orb/input_data/orb_companies2.csv' DELIMITER ';' CSV HEADER;")
    conn.commit()

    cur.execute("COPY export_branches FROM '/var/lib/orb/input_data/orb_branches2.csv' DELIMITER ';' CSV HEADER;")
    conn.commit()

    cur.execute("alter table export_companies drop column other_names, drop column other_naics_codes, drop column categories;")
    conn.commit()

    cur.execute("alter table export_companies add column parent_name text, add column branches_count bigint;")    
    conn.commit()

    cur.execute("update export_companies AS e SET parent_name=e2.name FROM export_companies e2 WHERE e2.company_id=e.parent_company_id;")
    conn.commit()

    cur.execute("update export_companies SET branches_count=(select count (branch_id) from export_branches where export_companies.company_id=export_branches.company_id group by export_branches.company_id);")
    conn.commit()

    cur.execute("alter table export_branches drop column index;")
    conn.commit()
 
    cur.execute("alter table export_companies drop column index;")
    conn.commit()

    sql = "COPY (SELECT * FROM export_companies) TO STDOUT WITH CSV DELIMITER ',' HEADER;"
    with open("input_data/companies.csv", "w") as file:
        cur.copy_expert(sql, file)

    sql2 = "COPY (SELECT * FROM export_branches) TO STDOUT WITH CSV DELIMITER ',' HEADER;"
    with open("input_data/branches.csv", "w") as file:
        cur.copy_expert(sql2, file)

    cur.close()
    conn.close()
