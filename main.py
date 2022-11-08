import json

import requests
import test_flight_1
from websocket import create_connection

HTTP_SERVER_URL = 'http://127.0.0.1:8000/'
WS_SERVER_URL = 'ws://127.0.0.1:8000/'
UUID = "123456789"


def check_missions():
    resource = requests.post(HTTP_SERVER_URL + 'check_missions/', json.dumps(dict(uuid=UUID)))
    data = resource.json()
    return data['has_mission']


def main():
    while True:
        has_mission = check_missions()
        if has_mission:
            break
    ws = create_connection(WS_SERVER_URL + "ws/")
    ws.send(json.dumps({"message": 'test'}))
    result = ws.recv()
    print(result)
    ws.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        test_flight_1.main()
