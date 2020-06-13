import pandas as pd

def write_Excel_file(df, sf, out, log_file):
    with pd.ExcelWriter(out, datetime_format='mmm d yyyy hh:mm:ss') as writer: #pylint: disable=abstract-class-instantiated
        df.to_excel(writer, sheet_name='raw data', index=False)
        sf.to_excel(writer, sheet_name='session data', index=False)
    with open(log_file, 'a+') as log:
        log.write(f'\nData written to Excel file: {out}')