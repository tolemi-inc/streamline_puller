import argparse
import json
import logging
import traceback
from typing import Any, Dict

from config import Config
from config_error import ConfigError

from streamline_puller.streamline_v1 import StreamlineV1
from streamline_puller.streamline_v2 import StreamlineV2

parser = argparse.ArgumentParser(description="Process inputs for community core pulls")

parser.add_argument("--config", type=str, help="Path to config file")

args = parser.parse_args()

logging.getLogger().setLevel(logging.INFO)


def run(config: Config) -> Dict[str, Any]:
    # Initialize the appropriate Streamline client based on version
    if config.version == "v1":
        streamline = StreamlineV1(
            config.client_id,
            config.client_secret,
            config.tenant_id,
            config.subscription_key,
        )
    else:  # v2
        streamline = StreamlineV2(
            client_id=config.client_id,
            subscription_key=config.subscription_key,
            username=config.username,
            password=config.password,
        )

    if config.version == "v1":
        include_historical_data = config.include_historical_data == "Yes"
        if config.report_name == "Inspections":
            headers_dict = streamline.create_inspection_report(
                config.data_file_path, include_historical_data
            )
        elif config.report_name == "Violations":
            headers_dict = streamline.create_violations_report(config.data_file_path)
        elif config.report_name == "Permits":
            headers_dict = streamline.create_permits_report(config.data_file_path)
    elif config.version == "v2":
        if config.report_name == "Inspections":
            headers_dict = streamline.create_inspection_report(config.data_file_path)
        elif config.report_name == "Occupancies":
            headers_dict = streamline.create_occupancy_report(config.data_file_path)
    else:
        raise ValueError(f"Invalid version: {config.version}")

    output_object = {
        "status": "ok",
        "file_name": config.data_file_path,
        "columns": headers_dict,
    }
    print("DONE", json.dumps(output_object))


def fail(error: Exception) -> Dict[str, Any]:
    result = {
        "status": "error",
        "error": """{}
         {}""".format(
            str(error), traceback.format_exc()
        ),
    }

    output_json = json.dumps(result)
    print("DONE", output_json)


def load_config(file_path: str) -> Config:
    raw_config = load_json(file_path)

    sub_config = raw_config.get("config", {})

    client_id = sub_config.get("client_id", None)
    client_secret = sub_config.get("client_secret", None)
    tenant_id = sub_config.get("tenant_id", None)
    subscription_key = sub_config.get("subscription_key", None)
    report_name = sub_config.get("report_name", None)
    include_historical_data = sub_config.get("include_historical_data", None)
    data_file_path = raw_config.get("dataFilePath", None)
    version = sub_config.get("version", "v1")  # Default to v1 for backward compatibility
    username = sub_config.get("username", None)
    password = sub_config.get("password", None)

    return Config(
        client_id,
        client_secret,
        tenant_id,
        subscription_key,
        report_name,
        include_historical_data,
        data_file_path,
        version,
        username,
        password,
    )


def load_json(file_path: str) -> Dict[str, Any]:
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: Config file '{file_path}' not found.")
        raise ConfigError(f"Config file '{file_path}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        raise ConfigError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        print(f"Error: Failed to load config file: {e}")
        raise ConfigError(f"Failed to load config file: {e}")


# Main Program
if __name__ == "__main__":
    try:
        config = load_config(args.config)
        run(config)
    except ConfigError as e:
        fail(e)
