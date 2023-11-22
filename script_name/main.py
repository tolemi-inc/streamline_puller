import json
import traceback
import argparse

parser = argparse.ArgumentParser(
    description='Process inputs')

parser.add_argument('--config', type=str, help='Path to config file')

args = parser.parse_args()


def run(config):
    data_file_path = config.data_file_path
    headers_dict = {'HEADERNAME', 'POSTGRES HEADER TYPE'}

    output_object = {'status': 'ok',
                     'file_name': data_file_path, 'columns': headers_dict}
    print('DONE', json.dumps(output_object))


def fail(error):
    result = {
        "status": "error",
        "error": """{}
         {}""".format(str(error), traceback.format_exc())
    }

    output_json = json.dumps(result)
    print('DONE', output_json)


def load_config(file_path):
    raw_config = load_json(file_path)
    # print('RAW CONFIG', raw_config)

    data_file_path = raw_config.get('dataFilePath', None)

    sub_config = raw_config.get('config')

    return Config(data_file_path)


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        True
        print(f"File '{file_path}' not found.")
    except json.JSONDecodeError as e:
        True
        print(f"JSON decoding error: {e}")
    except Exception as e:
        True
        print(f"An error occurred: {e}")


class ConfigError(Exception):
    def __init__(self, message):
        super().__init__(message)


class Config:
    def __init__(self, data_file_path):
        self.data_file_path = data_file_path

    @ property
    def data_file_path(self):
        return self._data_file_path

    @ data_file_path.setter
    def data_file_path(self, value):
        if value is None:
            raise ConfigError("Missing data file path in config.")
        else:
            self._data_file_path = value


# Main Program
if __name__ == "__main__":
    try:
        config = load_config(args.config)
        run(config)
    except ConfigError as e:
        fail(e)
