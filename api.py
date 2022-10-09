from flask import (
    Flask, 
    jsonify
)

import requests
import time


# Function that create the app 
def create_app(test_config=None ):
    # create and configure the app
    app = Flask(__name__)

    # Simple route
    @app.route('/')
    def hello_world(): 
        return jsonify({
           "status": "success",
            "message": "I am a Gas Bot!"
        }) 
    @app.route('/data')

    def main():
        #Get gas and current block
        get_gas()
        #Get data and filter for relevant inro 
        get_data()

        return jsonify({
            'data': [{"Current Gas": globals()["fast_gas"]}, {"Avg Gas": globals()["average"]}, {"First Trigger": globals()["first_trigger"]}, {"Max Gas": globals()["max_value"]}, {"Bots Included": globals()["list_length"]},{"Block Number": globals()["recent_block"]}]
        }) 


    def get_data():
        global average
        while True:
            #Check the last 5 minutes of blocks for GNS transactions
            try:
                request = requests.get(f'https://api.polygonscan.com/api?module=account&action=txlist&address=0x65187FeC6eCc4774C1f632C7503466D5B4353Db1&startblock={globals()["block"]}&endblock=lastest&page=1&offset=500&sort=asc&apikey=IZUPHCZBIENYCWHAMN5BS1FDMBFNYQ7W15').json()
            except requests.RequestException:
                print("RequestException from data grab")
                continue

            #A list to hold all sucsesful execute NFT transactios
            list1 = []
            #A list to hold the last blocks bots gas fees 
            list2 = []

            #Filter for NFT orders that are not faliures
            for result in request["result"]:
                result_name = result["functionName"]
                error = result["isError"]
                func_name = "executeNftOrder"
                if func_name in result_name and error != "1":
                    list1.append(result)


            #Check if my list has any results for the last 5 min
            if len(list1) == 0:
                #If no results, there were no sucsesful NFT executions in the last 5 min
                #So take away another 5 min of blocks and update the list1
                print("waiting")
                #Wait for 200 milliseconds because of Polygonscan API limit (5 per sec)
                time.sleep(.2)
                #Take away 5 minutes of blocks and call API again
                globals()["block"] = globals()["block"] - 150
                continue
            else:
                #Get the sum of the list
                global recent_block
                #reverse the list to bring most recent transaction to the front
                list1.reverse()
                recent_block = list1[0]["blockNumber"]
                for item in list1:
                    this_block = item["blockNumber"]
                    #filter out all transaction that are not included in the recent block
                    if this_block == recent_block:
                        #add them to list two
                        list2.append(float(item["gasPrice"])/10e8)
                #Set globals for data printing
                global first_trigger
                list2.reverse()
                first_trigger = list2[0]
                first_trigger = float(first_trigger)
                global list_length
                list_length = len(list2)
                global max_value
                max_value = max(list2)
                #average list2
                average = sum(list2[0:len(list2)]) / len(list2)
                break


    def get_gas():
        global block
        global fast_gas
        while True:
            try:
                request = requests.get("https://gasstation-mainnet.matic.network/v2").json()
            except requests.RequestException:
                print("RequestException from GetGas")
                continue
            block = (int(request["blockNumber"]) - 150)
            #return gas and 5 min worth of blocks
            fast_gas = (float(request["fast"]["maxPriorityFee"]))
            break       
    
    return app

APP = create_app()

if __name__ == '__main__':
    # APP.run(host='0.0.0.0', port=5000, debug=True)
    APP.run(debug=True)