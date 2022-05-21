# Binary data analysis of brain activity in mice
Python script for processing binary data analysis of brain activity in mice and exporting to CSV as desire

# 🐭 Usage

1. By default the script will fetch the files in the `Data` folder.

```
python BinaryDataAnalysis.py
```
 3. After running the script a csv file will be created inside the folders located in the specified path. The name of the csv file will be the date and time it was scanned.


# ⚙️ Modifiable parameters

Inside the script is possible to change following parameters as desired: 

- `FOLDER_WITH_BFthinned_FILES`: Root directory where the folders with the Fthinned and Bthinned files are.
- `SECONDS_PREVIOUS_TO_ONEs_BURST` : If set to `-1` the script will fetch all 0s before a burst of 1s. Otherwise, it will get the number of 0s corresponding to the specified seconds. Default is `10`.
- `START_ROW` : Row to start reading data (to avoid errors in the first values. Default value is `10`.
- `BINARY_DATA_COLUMN_FOR_B_THINNED_FILES`: Column from Bthinned file which have the binary data. Default is `9`.
- `TIMESTAMP_DATA_COLUMN_FOR_F_THINNED_FILES`: Column from Fthinned which have the timestamp. Default is `0`.
- `ACTIVITY_DATA_COLUMN_FOR_F_THINNED_FILES `: Column from Fthinned which have the activity data. Default is `1`.
