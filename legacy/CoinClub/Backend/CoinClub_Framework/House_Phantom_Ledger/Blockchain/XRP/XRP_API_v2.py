
###################### EXPERIMENTAL ######################

#Depricated :(
class RIPPLE_XRP_API:
    def __init__(self):
        print("Initialize XRP API class")

    def BASIC_XRP_API(self,VAR):
        today = date.today()
        NOW = today.strftime("%Y/%m/%d")
        Compile = 'https://data.ripple.com/v2%s' % VAR

        XRP_API_List = ["/accounts",
                        "/transactions",
                        "/network/exchange_volume",
                        "/network/external_markets",
                        "/network/xrp_distribution",
                        "/network/topology",
                        "/network/topology/nodes",
                        "/network/topology/links",
                        "/network/validators",
                        "/network/validator_reports",
                        "/network/rippled_versions",
                        "/normalize",
                        "/network/top_markets",
                        "/network/top_currencies",
                        "/gateways"]

        for i in XRP_API_List:
            print(i)
            if i == str(VAR):
                if VAR == "/network/top_currencies":
                    VAR = "/network/top_currencies/%s" % NOW
                if VAR == "/network/top_markets":
                    VAR = "/network/top_markets/%s" % NOW

                print("Pull_XRP_API")

                print(Compile)
                DATA = requests.get(Compile).json()
                print(Compile)
                return DATA


    def ACCOUNTS_XRP_API(self,addy,type): #[payments,exchanges]
        print("Pull_XRP_API")
        today = date.today()
        NOW = today.strftime("%Y/%m/%d")
        print(NOW)

        #Accounts
        payments = "/accounts/%s/payments" % addy
        exchanges = "/accounts/%s/exchanges" % addy
        transactions = "/accounts/%s/transactions"
        balance_changes = "/v2/accounts/%s/balance_changes"
        balances = "/accounts/%s/balances"
        orders = "/accounts/%s/orders"
        statstransactions ="accounts/%s/stats/transactions"
        statsvalue = "/accounts/%s/stats/value"
        accounts = "/accounts/%s"
        reports = "/reports/%s" % NOW

        Type_list = ["payments",
                    "exchanges",
                    "transactions",
                    "balance_changes",
                    "balances",
                    "orders",
                    "stats/transactions",
                    "stats/value",
                    "accounts",
                    "reports"]

        print(len(Type_list))
        print(Type_list)

        for i in range(0,(len(Type_list))):
            print(i)
            print(Type_list[i])
            if type == Type_list[i]:
                type = "/accounts/%s/%s" % (addy,Type_list[i])
                Compile = 'https://data.ripple.com/v2%s' % type
                print(Compile)
                DATA = requests.get(Compile).json()

                #print(DATA)
                return DATA

####################### TEST CODE w/ {:pubkey} #######################
    def VALIDATOR_XRP_API(self,type,pubkey): #{:pubkey}
        print("Pull_Validator_XRP_API")

        validators = "/validators/%s" % pubkey
        manifest = "/validators/%s/manifests" % pubkey
        reports = "/validators/%s/reports" % pubkey

        Validator_List = ["validators",
                          "manifest",
                          "reports"]

        print(type)
        for i in range(0,len(Validator_List)):
            #print(Validator_List[i])
            if str(Validator_List[i]) == type:
                Compile = "http://data.ripple.com/v2/network/validators/%s/%s" % (pubkey,type)
                print("this is " ,Compile)

                DATA = requests.get(Compile).json()
                print(Compile)
                return DATA

    def STATS(self): # healthcheck & Transaction Statistics
        print("Pull_XRP_API")
