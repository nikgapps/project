import json
import requests
from NikGapps.helper.Statics import Statics


class Requests:

    @staticmethod
    def get(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        return requests.get(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def put(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        return requests.put(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def patch(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        return requests.patch(url, data=json.dumps(params), headers=headers)

    @staticmethod
    def post(url, headers=None, params=None):
        if params is None:
            params = {"": ""}
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:105.0) Gecko/20100101 Firefox/105.0'}
        return requests.post(url, data=json.dumps(params), headers=headers)

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
    def get_folder_access():
        decoded_hand = Requests.get(Statics.folder_access_url)
        if decoded_hand.status_code == 200:
            data = decoded_hand.json()
            return data
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
