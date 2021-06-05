from Reference.File_Manager import *
from Reference.Cloud import *
from Reference.XMLcc import *
from Reference.XRPcc import *

class Live_Gateway:
    def __init__(self):
        print("Prime Gateway")
        self.LIVE()

    def GATEWAY(self):
        print("Start Gateway")

    def LIVE(self):
        print("-- LIVE --")

class App_Engine:
    def __init__(self):
        print("Start App Engine")
        
    def TEST_APP_ENGINE(self):
        print("Start Test App Engine")

if "__main__" == __name__:
    Live_Gateway()
