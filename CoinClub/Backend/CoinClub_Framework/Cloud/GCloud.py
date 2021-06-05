import gspread
import yaml

class GSheets
    def PULL_FROM_GSHEETS(count):
        with open('Config/Cloud_Config.yaml', 'r') as f:
            doc = yaml.load(f, Loader=yaml.FullLoader)
            Sheet = doc["GCloud"]["Sheet"]

        scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        secrets ='Keys/GSheet_Keys/client_secret.json'

        creds = ServiceAccountCredentials.from_json_keyfile_name(secrets, scope)
        client = gspread.authorize(creds)

        sheet = client.open(str(Sheet)).sheet1

        # Extract and print all of the values
        list_of_hashes = sheet.get_all_records()
        go = json.dumps(list_of_hashes, sort_keys=True, indent=1)
        pprint(go)
        return go

    def PUSH_TOO_GSHEETS():
        print("test")
