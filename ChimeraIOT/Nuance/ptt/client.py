import json
import requests
import sys

from pprint import pprint

service = sys.argv[1]

headers = {
    'NMSP_APPID': sys.argv[2],
    'NMSP_KEY': sys.argv[3],
    'NMSP_LANGUAGE': sys.argv[4],
    'NMSP_USER': sys.argv[5]
}

params = {
    'appid': sys.argv[2],
    'key': sys.argv[3],
    'language': sys.argv[4],
    'user': sys.argv[5]
}

base_url = 'http://localhost:8080'
if service == 'nlu':
    url = base_url + '/nlu'
    headers['NMSP_TAG'] = sys.argv[6]
    params['tag'] = sys.argv[6]
elif service == 'asr':
    url = base_url + '/asr'
    headers['NMSP_RECOGNITION_TYPE'] = sys.argv[6]
    params['recognition_type'] = sys.argv[6]
elif service == 'tts':
    url = base_url + '/tts'
    body = sys.argv[6]

if service == 'tts':
    requests.post(url, headers=headers, data=body)
else:
    response = requests.get(url, params=params, stream=True)
    for message in response.iter_content(None):
        print(message.decode('utf-8'))
