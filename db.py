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

    branches = pd.read_csv('input_data/orb_branches2.csv')
    companies = pd.read_csv('input_data/orb_companies2.csv')

    conn = psycopg2.connect(
        host='localhost', 
        port=54320, 
        dbname='postgres',
        user='postgres',
    )

    cur = conn.cursor()

    engine = create_engine('postgresql://postgres@localhost:54320/postgres')

    branches.to_sql('export_branches', engine)
    companies.to_sql('export_companies', engine)

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
