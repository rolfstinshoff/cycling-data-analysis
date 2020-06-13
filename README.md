# cycling-data-analysis
This is an ongoing Python project for the analysis of cycling ride(s) from .fit files, i.e. generated by wahoo or Garmin devices. It will plot an overview of your ride (altitude, speed, heart rate profile), a heart rate and altitude distribution, a pie plot of your heart rate zones as well as a data summary table of your ride stats. In addition, you can plot a heart rate heatmap in google maps, output your ride data into an Excel file or store your data in an SQL database.

## Running locally
You can clone the repository to try it out:

```
$ git clone https://github.com/rolfstinshoff/cycling-data-analysis.git
```

The following Python dependencies are required:

```
$ pip install fitdecode
```

An API key is required for google maps. You can get one here: 

[https://developers.google.com/maps/documentation/javascript/get-api-key](https://developers.google.com/maps/documentation/javascript/get-api-key)

Furthermore, you will have to create a .env file on the top level for your API key and to specify some path variables:
```
GOOGLE_MAPS_API_KEY
FIT_FILE_FOLDER_PATH
LOG_FILE_PATH
EXCEL_OUTPUT_PATH
```

### Monitoring your workout folder (macOS only)
The folder `daemon` contains an example plist file for a launch agent in order to run the script when a new workout file is added to your folder. 

## To be added
Include power data analysis (because I don't have a power meter yet)