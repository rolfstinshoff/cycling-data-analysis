import sqlite3
from sqlite3 import Error
import glob, os
import data.reader as dr
import pandas as pd
import numpy as np
from ast import literal_eval as make_tuple

def check_if_db_exists(db, data_fields, session_fields, log_file):
    if os.path.isfile(db):
        try:
            con = sqlite3.connect(db)
            cur = con.cursor()
            cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='raw_data' ''')
            if cur.fetchone()[0]==1 : 
                with open(log_file, 'a+') as log:
                    log.write(f'\nInitial database has been found')
                return
            else :
                cur.execute("CREATE TABLE IF NOT EXISTS raw_data(%s)" % ", ".join(data_fields))
                cur.execute("CREATE TABLE IF NOT EXISTS session_data(%s)" % ", ".join(session_fields))
                con.commit()
                con.close()
                with open(log_file, 'a+') as log:
                    log.write(f'\nInitial database created: {db}')
                return

        except Error as err:
            with open(log_file, 'a+') as log:
                log.write(f'\nCould not connect to database. The following error occured:\n{err}')

    else:
        try:
            con = sqlite3.connect(db)
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS raw_data(%s)" % ", ".join(data_fields))
            cur.execute("CREATE TABLE IF NOT EXISTS session_data(%s)" % ", ".join(session_fields))
            con.commit()
            con.close()
            with open(log_file, 'a+') as log:
                log.write(f'\nInitial database created: {db}')

        except Error as err:
            with open(log_file, 'a+') as log:
                log.write(f'\nCould not connect to database. The following error occured:\n{err}')


def save_data_to_db(df, sf, file, log_file, db):
    try:
        con = sqlite3.connect(db)
        df.to_sql('raw_data', con, if_exists="append", index=False)
        # SQL can't store tuples so we convert it to string in order to be able to write it to the db.
        # Don't forget to turn it back into a tuple when you read the data from db into a dataframe!!!
        if 'time_in_hr_zone' in sf:
            sf['time_in_hr_zone'] = sf['time_in_hr_zone'].apply(str)
        sf.to_sql('session_data', con, if_exists='append', index=False)
        con.commit()
        con.close()
        with open(log_file, "a+") as log:
             log.write(f"\nData set written to database. File path: {file}")

    except Error as err:
        with open("log.txt", "a+") as log:
             log.write(f"\nCould not connect to database. The following error occured:\n{err}\n{file} not written to the database")


# write all existing .fit files in your folder to db
def save_all(folder_path, log_file, db):
    for file in glob.glob(os.path.join(folder_path, '*.fit')):
        df, sf = dr.retrieve_data(file, log_file)
        dr.calculate(df, sf)
        save_data_to_db(df, sf, file, log_file, db)


def read_from_database(db):
    con = sqlite3.connect(db)
    sql = """SELECT * FROM session_data WHERE timestamp BETWEEN '2020-06-01' AND '2020-06-26';"""
    sf = pd.read_sql(sql, con).replace([None], np.nan)
    sf['time_in_hr_zone'] = sf['time_in_hr_zone'].apply(lambda x: make_tuple(x) if type(x) == str else np.nan)
    return sf