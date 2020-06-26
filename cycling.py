import os, sys, glob, datetime
import dotenv as dot
import matplotlib.pyplot as plt
import pandas as pd
import data.reader as dr
import data.export as de
import plotter.ride_analysis as ride
import data.database as db
from data.reader import data_fields, session_fields

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# load your paths from .env file
dot.load_dotenv()
fit_folder = os.getenv('FIT_FILE_FOLDER_PATH')
log_file = os.getenv('LOG_FILE_PATH')
excel_out = os.getenv('EXCEL_OUTPUT_PATH')
database = os.getenv('DATABASE_FILE_PATH')

# get the latest file in your folder of workouts
file_path = max(glob.iglob(fit_folder + '/*.fit'), key=os.path.getctime)
filename = os.path.basename(file_path)
path_dir = os.path.dirname(file_path)
excel_out += filename.replace('.fit', '.xlsx')

with open(log_file, 'a+') as log:
    log.write(f'Script started running at: {datetime.datetime.now()}')

# read the .fit file
dframe, sessionframe = dr.retrieve_data(file_path, log_file)
dr.calculate(dframe, sessionframe)

# plot the ride analysis
ride.plot_google_map(dframe, log_file)
ride.plot_analysis_adjusted(dframe, sessionframe, filename, log_file)
data_table = ride.render_data_table(ride.create_data_table(sessionframe))

# create the initial database
db.check_if_db_exists(database, data_fields, session_fields, log_file)

# write your data to a db and/or Excel file
# de.write_Excel_file(dframe, sessionframe, excel_out, log_file)
db.save_data_to_db(dframe, sessionframe, filename, log_file, database)

# hr_zones = db.read_from_database(database)

# run only this command if you want to load all your rides into a db
# db.save_all(path_dir, log_file, database)

with open(log_file, 'a+') as log:
    log.write(f'\nFinished processing at: {datetime.datetime.now()}\n\n\n')

plt.show()
plt.close()