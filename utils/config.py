import json, os

json_file_path = os.path.join(os.path.dirname(__file__), 'password.json')

with open(json_file_path, 'r') as json_file:
    loaded_pw = json.load(json_file)

WHEREDB_CONFIG = {
    'dbHost': '34.64.179.49',
	'dbPort': 5432,
	'dbUser': "postgres",
	'dbPassword': loaded_pw[0]["dbPassword"],
	'dbName': "whereDB"
}

PERFORCHKDB_CONFIG = {
    'dbHost': '43.202.56.193',
	'dbPort': 5431,
	'dbUser': "lucy",
	'dbPassword': loaded_pw[1]["dbPassword"],
	'dbName': "performchk"
}