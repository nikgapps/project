import json
import os


class Json:

    @staticmethod
    def print_json_dict(json_dict):
        print(json.dumps(json_dict, indent=2, sort_keys=True))

    @staticmethod
    def write_dict_to_file(json_dict, file_name):
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))
        try:
            with open(file_name, 'w') as file:
                json_dumps_str = json.dumps(json_dict, indent=4, sort_keys=True)
                print(json_dumps_str, file=file)
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def read_dict_from_file(file_name):
        try:
            if not os.path.exists(file_name):
                return {}
            with open(file_name, 'r') as file:
                json_dict = json.load(file)
                return json_dict
        except Exception as e:
            print(e)
            return None
