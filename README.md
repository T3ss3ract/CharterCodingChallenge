# Coding Challenge:

to install requirements, type `pip3 install -r requirements.txt`

to run, cd into directory and type `python3 rest_api.py`

to hit endpoints, type either `http://127.0.0.1:3751/json/<orgname:relcount:labor>` for the json endpoint
or `http://127.0.0.1:3751/csv/<orgname:relcount:labor>` for a csv download. 

the db.json file is needed to parse the data, while the sorted_file.csv is generated when the program starts
and changes along with the csv endpoint request. When the json endpoint is hit, the data will be printed to the
terminal.