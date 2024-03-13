from streamline import Streamline
from config import Config
from config_error import ConfigError
import traceback
import logging
import argparse
import json
import csv

parser = argparse.ArgumentParser(description="Process inputs for community core pulls")

parser.add_argument("--config", type=str, help="Path to config file")

args = parser.parse_args()

logging.getLogger().setLevel(logging.INFO)


def run(config):

    streamline = Streamline(config.client_id, config.client_secret, config.tenant_id, config.subscription_key, "https://data.streamlineapi.com/")

    token = streamline.getToken()

    include_historical_data = (config.include_historical_data == "Yes")
    if config.report_name == 'Inspections':
        streamline.create_inspection_report(token, config.data_file_path, include_historical_data)
    elif config.report_name == 'Violations':
        streamline.create_violations_report(token, config.data_file_path)
    elif config.report_name == 'Permits':
        streamline.create_permits_report(token, config.data_file_path, include_historical_data)

    with open(config.data_file_path, 'r+') as csvfile:
        headers_dict = [{"name": header, "type": "VARCHAR"} for header in csvfile.readline().split(',')]
        
        all_lines = csvfile.readlines()
        data_lines = all_lines[1:-1]

        csvfile.seek(0)
        csvfile.truncate()
        csvfile.writelines(data_lines)

    output_object = {
        "status": "ok",
        "file_name": config.data_file_path,
        "columns": headers_dict
    }
    print("DONE", json.dumps(output_object))

def fail(error):
    result = {
        "status": "error",
        "error": """{}
         {}""".format(
            str(error), traceback.format_exc()
        ),
    }

    output_json = json.dumps(result)
    print("DONE", output_json)


def load_config(file_path):
    raw_config = load_json(file_path)

    sub_config = raw_config.get("config", {})

    client_id = sub_config.get("client_id", None)
    client_secret = sub_config.get("client_secret", None)
    tenant_id = sub_config.get("tenant_id", None)
    subscription_key = sub_config.get("subscription_key", None)
    report_name = sub_config.get("report_name", None)
    include_historical_data = sub_config.get("include_historical_data", None)
    data_file_path = raw_config.get("dataFilePath", None)


    return Config(client_id, client_secret, tenant_id, subscription_key, report_name, include_historical_data, data_file_path)


def load_json(file_path):
    try:
        with open(file_path, "r") as file:
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


# Main Program
if __name__ == "__main__":
    try:
        config = load_config(args.config)
        run(config)
    except ConfigError as e:
        fail(e)

