from FORMAT import Config
class Strategies:
    def __init__(self):
        print("Start Algo")

        #self.Liquid(1.5,0.25,10)
        self.Liquid_Mean(1,0.015,3)

    def Liquid(self,Price,Deviation,set,count=0):
        if count == 0:
            Current_Price = Price
            Config.Config_file()
            
        if count <= set:
            print(Price)
            self.Liquid(Price+Deviation,Deviation,set,count+1)
        else:
            print("END")

    def Liquid_Mean(self,Price,Deviation,set,count=0):
        self.Liquid(Price,Deviation,set,count)
        self.Liquid(Price,-Deviation,set,count)

    def Liquid_Top(self,Price,Deviation,set,count=0):
        self.Liquid(Price,-Deviation,set,count)

    def Liquid_Bottom(self,Price,Deviation,set,count=0):
        self.Liquid(Price,Deviation,set,count)

    def Liquid_Stable_Narrow():
        print("start func to x degrees of seperation")

    def Liquid_Stable_Wide():
        print("start func to x degrees of seperation")

class TradeRange_Execute:
    def __init__(self):
        print("Start Algo")

    def DayRangeLiquidity():
        print("test")

    def WeekRangeLiquidity():
        print("test")

    def MonthRangeLiquidity():
        print("test")

class Execute:
    def __init__(self):
        print("Execute")

if "__main__" == __name__:
    Strategies()
