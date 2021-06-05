import requests

class Call_API:
    def API_GET_Call(url,call):
        Compile = "%s%s" % (url,call)
        DATA = requests.get(Compile).json()
        print("API URL: %s" % Compile)
        return DATA

    def API_POST_Call(url,myobj):
        x = requests.post(url, data = myobj)
        return x.text
