import json
import time

import requests
from NikGapps.helper.Statics import Statics


class Requests:

    @staticmethod
    def get(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        result = requests.get(url, data=json.dumps(params), headers=headers)
        if result.status_code == 429:
            Requests.handle_429_response(result)
            return requests.get(url, data=json.dumps(params), headers=headers)
        return result

    @staticmethod
    def put(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        result = requests.put(url, data=json.dumps(params), headers=headers)
        if result.status_code == 429:
            Requests.handle_429_response(result)
            return requests.put(url, data=json.dumps(params), headers=headers)
        return result

    @staticmethod
    def patch(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        result = requests.patch(url, data=json.dumps(params), headers=headers)
        if result.status_code == 429:
            Requests.handle_429_response(result)
            return requests.patch(url, data=json.dumps(params), headers=headers)
        return result

    @staticmethod
    def post(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        result = requests.post(url, data=json.dumps(params), headers=headers)
        if result.status_code == 429:
            Requests.handle_429_response(result)
            return requests.post(url, data=json.dumps(params), headers=headers)
        return result

    @staticmethod
    def get_text(url):
        return requests.get(url).text

    @staticmethod
    def get_release_date(android_version, release_type):
        decoded_hand = Requests.get(Statics.release_tracker_url)
        if decoded_hand.status_code == 200:
            data = decoded_hand.json()
            if android_version in data[release_type]:
                return data[release_type][android_version]
        else:
            print(f"{decoded_hand.status_code} while getting release date")
            return Statics.time

    @staticmethod
    def get_folder_access(folder_name=None):
        decoded_hand = Requests.get(Statics.folder_access_url)
        if decoded_hand.status_code == 200:
            data = decoded_hand.json()
            return data if folder_name is None else (data[folder_name] if folder_name in data else None)
        else:
            print(f"{decoded_hand.status_code} while getting folder access")
            return None

    @staticmethod
    def get_admin_access():
        decoded_hand = Requests.get(Statics.admin_access_url)
        admin_list = []
        if decoded_hand.status_code == 200:
            for admin in decoded_hand.text.split("\n"):
                if admin != "":
                    admin_list.append(admin)
            return admin_list
        else:
            print(f"{decoded_hand.status_code} while getting admin access")
            return ["nikhilmenghani", "nikgapps"]

    @staticmethod
    def handle_429_response(result):
        if 'Retry-After' in result.headers:
            print(f"Sleeping for {result.headers['Retry-After']} seconds")
            time.sleep(float(result.headers['Retry-After']))
        else:
            print(f"Sleeping for 120 seconds")
            time.sleep(120)
