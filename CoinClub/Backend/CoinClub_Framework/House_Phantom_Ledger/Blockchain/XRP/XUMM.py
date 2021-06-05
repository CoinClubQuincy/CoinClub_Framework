import requests
########################### TEST!!!!
class Basic_API:
    def GET_API(api_var):
        print("start func")
        #Function [payload_uuid,custom_identifier,payload_uuid,token,ping,curated-assets,txid,kyc-status,payload]
        url = "https://xumm.app/api/v1/platform/payload/%s" % api_var
        response = requests.request("GET", url)
        return response.text
##################

class Functions:
    def KYC_STATUS():
        url = "https://xumm.app/api/v1/platform/kyc-status"
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, headers=headers)
        return response.text

    def PAYLOAD(txblob,submit,multisign,expire): #"txblob": "Optional HEX transaction template"
        url = "https://xumm.app/api/v1/platform/payload"
        payload = {
            "txblob": "%s" % txblob,
            "options": {
                "submit": "%s" % submit,
                "multisign": "%s" % multisign,
                "expire": "%s" % expire
            }
        }

        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers)
        return response.text

    def EVENT(user_token,subtitle,body,tx,account):
        payload = {
        	"user_token": "%s" % user_token,
        	"subtitle": "%s" % subtitle,
        	"body": "%s" % body,
        	"data": {
        		"tx": "%s" % tx,
        		"account": "%s" % account
        	}
        }

        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers)
        return response.text

    def PUSH(user_token,subtitle,body,JSON_data):
        url = "https://xumm.app/api/v1/platform/payload"
        payload = {
        	"user_token": "%s" % user_token,
        	"subtitle": "%s" % subtitle,
        	"body": "%s" % body,
        	"data": {
        		"Title": "%s" % JSON_data
        	}
        }
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers)
        return response.text

class VAR_OUTPUT:
    def VAR_PAYLOAD(DATA):
        Item = json.load(DATA)

    def VAR_GET_PAYLOAD_UUID(DATA):
        Item = json.load(DATA)

    def VAR_CUSTOM_IDENTIFIER(DATA):
        Item = json.load(DATA)

    def VAR_ENTER_PAYLOAD_UUID(DATA):
        Item = json.load(DATA)

    def VAR_TOKEN(DATA):
        Item = json.load(DATA)

    def VAR_EVENT(DATA):
        Item = json.load(DATA)

    def VAR_PUSH():
        Item = json.load(DATA)
        pushed =  Item["result"]
        return pushed

    def VAR_PING(DATA):
        Item = json.load(DATA)

    def VAR_CURATED_ASSETS(DATA):
        Item = json.load(DATA)

    def VAR_XRPL_TX_ID(DATA):
        Item = json.load(DATA)

    def VAR_KYC_STATUS(DATA):
        Item = json.load(DATA)
