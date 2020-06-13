import sqlite3
from sqlite3 import Error
import glob, os
import data.reader as dr

def save_data_to_db(df, sf, file, log_file):
    try:
        con = sqlite3.connect("CyclingData.db")
        df.to_sql('raw_data', con, if_exists="append", index=True)
        # SQL can't store tuples so we convert it to string in order to be able to write it to the db.
        # Don't forget to turn it back into a tuple when you read the data from db into a dataframe!!!
        if 'time_in_hr_zone' in sf:
            sf['time_in_hr_zone'] = sf['time_in_hr_zone'].apply(str)
        sf.to_sql('session_data', con, if_exists='append', index=True)
        con.commit()
        con.close()
        with open(log_file, "a+") as log:
             log.write(f"\nData set written to database. File path: {file}")

    except Error as err:
        with open("log.txt", "a+") as log:
             log.write(f"\nCould not connect to database. The following error occured:\n{err}\n {file} not written to the database")

# write all existing .fit files in your folder to db
def save_all(folder_path, log_file):
    for file in glob.glob(os.path.join(folder_path, '*.fit')):
        df, sf = dr.retrieve_data(file, log_file)
        dr.calculate(df, sf)
        save_data_to_db(df, sf, file, log_file)