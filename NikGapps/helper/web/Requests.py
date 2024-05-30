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
            return Requests.handle_429_response(url, params, headers, result)
        return result

    @staticmethod
    def put(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        result = requests.put(url, data=json.dumps(params), headers=headers)
        if result.status_code == 429:
            return Requests.handle_429_response(url, params, headers, result)
        return result

    @staticmethod
    def patch(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        result = requests.patch(url, data=json.dumps(params), headers=headers)
        if result.status_code == 429:
            return Requests.handle_429_response(url, params, headers, result)
        return result

    @staticmethod
    def post(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        result = requests.post(url, data=json.dumps(params), headers=headers)
        if result.status_code == 429:
            return Requests.handle_429_response(url, params, headers, result)
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
    def get_package_details(android_version):
        package_details_url = f"https://raw.githubusercontent.com/nikgapps/tracker/main/{android_version}/GooglePackages.json"
        decoded_hand = Requests.get(package_details_url)
        package_details = {}
        if decoded_hand.status_code == 200:
            return decoded_hand.json()
        else:
            print(f"{decoded_hand.status_code} while getting package details")
            return package_details

    @staticmethod
    def get_appset_details(android_version):
        appset_details_url = f"https://raw.githubusercontent.com/nikgapps/tracker/main/{android_version}/AppSets.json"
        decoded_hand = Requests.get(appset_details_url)
        appset_details = {}
        if decoded_hand.status_code == 200:
            return decoded_hand.json()
        else:
            print(f"{decoded_hand.status_code} while getting appset details")
            return appset_details

    @staticmethod
    def handle_429_response(url, params, headers, result):
        if 'Retry-After' in result.headers:
            wait_time = float(result.headers['Retry-After'])
            print(f"Sleeping for {wait_time} seconds...")
            time.sleep(wait_time)
            return requests.get(url, data=json.dumps(params), headers=headers)
        else:
            for delay in [0, 1, 2, 4, 8, 16, 32, 64]:
                print(f"Rate limit exceeded. Waiting for {delay} seconds before retrying...")
                time.sleep(delay)
                result = requests.get(url, data=json.dumps(params), headers=headers)
                if result.status_code != 429:
                    return result
            return result
