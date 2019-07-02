import json
import os
import requests

WAKI_API_URL = 'https://api.waqi.info'
FEED_API_PATH = '/feed'
CDMI_PATH = '/cdmi'

def get_environment_variables():
    """Return a dict with the required environment variables"""
    vars = {}
    vars['ONEPROVIDER_HOST'] = os.environ.get('ONEPROVIDER_HOST').strip('/')
    vars['ONEDATA_ACCESS_TOKEN'] = os.environ.get('ONEDATA_ACCESS_TOKEN')
    vars['ONEDATA_SPACE'] = os.environ.get('ONEDATA_SPACE').strip('/')
    vars['ONEDATA_SPACE_FOLDER'] = os.environ.get('ONEDATA_SPACE_FOLDER').strip('/')
    vars['WAQI_TOKEN'] = os.environ.get('WAQI_TOKEN')
    return vars

def handle(req):
    vars = get_environment_variables()
    # Check if all variables are defined
    for var in vars:
        if not var:
            return 'You must define the environment variables'

    # Get WAQI station ID from path
    station_id = os.environ.get('Http_Path').strip('/')
    if not station_id:
        return 'Please, specify a station identifier in the path'

    # Get the station feed
    params = {'token': vars['WAQI_TOKEN']}
    url = f'{WAKI_API_URL}{FEED_API_PATH}/{station_id}/'

    r = requests.get(url, params=params)
    if (r.status_code is 200):
        data = r.json()
        if ('status' in data and
            data['status'].lower() is 'ok'):
            name = data['city']['name'].split(', ')[0]
            date = data['time']['s'].split(' ')[0]
            file_name = f'{name}{date}.json'

            json_data = json.dumps(data, indent=2)

            # Upload to Onedata space
            url = f'https://{vars['ONEPROVIDER_HOST']}{CDMI_PATH}/{vars['ONEDATA_SPACE']}/{vars['ONEDATA_SPACE_FOLDER']}/{file_name}'
            headers = {'X-Auth-Token': vars('ONEDATA_ACCESS_TOKEN')}

            r = requests.put(url, data=json_data, headers=headers)
            if r.status_code in [201, 202, 204]:
                return f'File "{file_name}" uploaded successfully to space "{vars['ONEDATA_SPACE']}" in Oneprovider "{vars['ONEPROVIDER_HOST']}"'
            else:
                return 'Error uploading file to Onedata'

    return 'Error getting station feed'
