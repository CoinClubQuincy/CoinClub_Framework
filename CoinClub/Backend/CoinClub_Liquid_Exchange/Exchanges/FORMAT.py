import requests
import json

class Call_API:
    def API_GET_Call(url,call):
        Compile = "%s%s" % (url,call)
        DATA = requests.get(Compile).json()
        return DATA

    def API_POST_Call(url,myobj):
        x = requests.post(url, data = myobj)
        return x.text

class Json:
    def json_write(file_name,Data):
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(Data, f, ensure_ascii=False, indent=4)

    def read_json(FILE):
        with open('%s' % FILE) as f:
          data = json.load(f)

        return data

class Config:
    def Config_file():
        print("place config data here")