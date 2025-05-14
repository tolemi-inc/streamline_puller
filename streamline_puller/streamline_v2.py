import json
from typing import Any, Dict, List, Optional

import pandas as pd
import requests


class StreamlineV2:
    """V2 implementation of Streamline API client."""

    def __init__(
        self,
        client_id: str,
        subscription_key: str,
        username: str = None,
        password: str = None,
    ):
        self.client_id = client_id
        self.subscription_key = subscription_key
        self.username = username or "integrations-scripts+toledo-streamline@tolemi.com"
        self.password = password or "w5$dK2_7?fA5_3$"
        self.base_url = "https://process-dev.firerecoveryusa.com/Primary/restapi"
        self._token = None
        self._token_expiry = None
        self.get_token()

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, json=data, headers=headers)
            response.raise_for_status()
            return response
        except Exception as e:
            raise Exception(f"Error making API request: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        token = self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "ClientID": self.client_id,
            "SubscriptionKey": self.subscription_key,
        }

    def get_token(self) -> str:
        # Check if we have a valid token
        if self._token:
            return self._token

        url = "https://process-dev.firerecoveryusa.com/Primary/Decisions/Primary/REST/AccountService/LoginAndGetJWTToken"
        params = {
            "outputType": "JSON",
            "userName": self.username,
            "password": self.password,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            result = response.json()

            if "LoginAndGetJWTTokenResult" not in result:
                raise Exception("Invalid token response format")

            token = result["LoginAndGetJWTTokenResult"]
            self._token = token

        except Exception as e:
            print(f"\nError: {str(e)}")
            if isinstance(e, requests.exceptions.RequestException) and hasattr(e, "response"):
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            print(f"URL being accessed: {url}")
            raise

    def get_occupancies(self, occupancy_type: str) -> pd.DataFrame:
        if occupancy_type == "commercial":
            endpoint = "/SLI/GeneralAPI/Occupancy/GetCommercialOccupancies"
        elif occupancy_type == "residential":
            endpoint = "/SLI/GeneralAPI/Occupancy/GetResidentialOccupancies"
        else:
            raise Exception("Invalid occupancy type")
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "ClientId": self.client_id,
            "SubscriptionKey": self.subscription_key,
        }
        payload_dict = {
            "outputtype": "Json",
            "IsDeleted": False,
            "IsVacantOccupancy": False,
        }
        payload = json.dumps(payload_dict)

        response = requests.request("POST", url, headers=headers, data=payload)
        if occupancy_type == "commercial":
            result = response.json()["Done"].get("CommercialOccupanciesList")
        elif occupancy_type == "residential":
            result = response.json()["Done"].get("ResidentialOccupanciesList")
        else:
            raise Exception("Invalid occupancy type")

        if not result:
            raise Exception("Invalid occupancies response format")

        return pd.DataFrame(result)

    def get_inspections(
        self,
        fiscal_year_id: int = None,
        occupancy_id: int = None,
        inspection_series_id: int = None,
        inspection_status_id: int = None,
    ) -> pd.DataFrame:
        endpoint = "/SLI/GeneralAPI/Inspection/GetCommercialOccupancyInspections"
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "ClientId": self.client_id,
            "SubscriptionKey": self.subscription_key,
        }
        inspection_request_object = {
            "FiscalYearId": fiscal_year_id,
            "Occupancy_id": occupancy_id,
            "InspectionSeriesId": inspection_series_id,
            "InspectionStatusId": inspection_status_id,
            "IsDeleted": False,
            "IsVacant": False,
        }
        payload_dict = {
            "outputtype": "Json",
            "CommercialOccupancyInspectionsRequest": inspection_request_object,
        }
        payload = json.dumps(payload_dict)

        response = requests.request("POST", url, headers=headers, data=payload)
        try:
            result = response.json()["Done"]["Result"]
        except:
            raise Exception("Invalid inspections response format")

        return pd.DataFrame(result)

    def create_inspection_report(self, data_file_path):
        inspections = self.get_inspections()

        for col in inspections.columns:
            try:
                inspections[col] = pd.to_numeric(inspections[col])
            except:
                inspections[col] = (
                    inspections[col].astype(str).str.replace(",", ".").str.replace("\r", "->")
                )
        print(f"Retrieved {len(inspections)} inspection records")

        print("Creating headers dictionary")
        headers_dict = [{"name": col, "type": "VARCHAR"} for col in inspections.columns]
        headers_dict.insert(0, {"name": "rn", "type": "VARCHAR"})

        print(f"Writing inspections data to {data_file_path}")
        inspections.to_csv(data_file_path, header=False)
        print("Successfully wrote inspections data to CSV")

        return headers_dict

    def create_occupancy_report(self, data_file_path, occupancy_type: str = "commercial"):
        print(f"Fetching {occupancy_type} occupancies data")
        occupancies = self.get_occupancies(occupancy_type)
        occupancies["AHJText"] = occupancies["AHJText"].replace(",", ".")

        for col in occupancies.columns:
            try:
                occupancies[col] = pd.to_numeric(occupancies[col])
            except:
                occupancies[col] = (
                    occupancies[col].astype(str).str.replace(",", ".").str.replace("\r", "->")
                )
        print(f"Retrieved {len(occupancies)} occupancy records")

        print("Creating headers dictionary")
        headers_dict = [{"name": col, "type": "VARCHAR"} for col in occupancies.columns]
        headers_dict.insert(0, {"name": "rn", "type": "VARCHAR"})

        print(f"Writing occupancies data to {data_file_path}")
        occupancies.to_csv(data_file_path, header=False)
        print("Successfully wrote occupancies data to CSV")

        return headers_dict
