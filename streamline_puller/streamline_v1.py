import datetime
import logging

import pandas as pd
import requests


class StreamlineV1:
    def __init__(self, client_id, client_secret, tenant_id, subscription_key):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.subscription_key = subscription_key
        self.base_url = "https://data.streamlineapi.com/"
        self.token = self.getToken()

    def make_api_call(self, method, url, headers, payload=None) -> requests.Response:
        try:
            if payload:
                response = requests.request(method, url, headers=headers, data=payload)
            else:
                response = requests.request(method, url, headers=headers)

            logging.info("Response: " + str(response.status_code) + ", " + response.reason)

            if response.status_code == 200:
                return response

            else:
                logging.error("Api request returned a non-200 response")
                try:
                    error_body = response.json()
                    logging.error(error_body)
                except Exception:
                    error_body = response.text
                raise Exception(
                    f"API request to {url} failed with status {response.status_code}: {error_body}"
                )

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request to {url} failed: {str(e)}") from e

    def getToken(self) -> str:
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": f"{self.client_id}/.default",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.make_api_call("POST", url, headers, payload)

        token_data = response.json()
        if "access_token" not in token_data:
            raise Exception(f"Token response missing 'access_token' field. Response: {token_data}")

        logging.info("Successfully got access token")
        return token_data["access_token"]

    def get_object(self, url_suffix, object_name) -> pd.DataFrame:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }
        url = f"{self.base_url}/{url_suffix}"
        response = self.make_api_call("GET", url, headers)

        logging.info(f"Successfully got {object_name}")

        if object_name == "Occupancy":
            return pd.DataFrame([response.json()])
        else:
            return pd.DataFrame(response.json()[object_name])

    def get_occupancies(self) -> pd.DataFrame:
        url_suffix = "occupancy/GetOccupancies/1/?PageIndex=1&PageCount=4000"
        return self.get_object(url_suffix, "Occupancies")

    def get_occupancy(self, occupancy_id) -> pd.DataFrame:
        url_suffix = f"occupancy/GetOccupancy/{occupancy_id}"
        return self.get_object(url_suffix, "Occupancy")

    def get_inspections(self) -> pd.DataFrame:
        url_suffix = "inspections/GetOccupancyInspections/0"
        return self.get_object(url_suffix, "OccupancyInspection")

    def get_violations(self) -> pd.DataFrame:
        url_suffix = "inspections/GetInspectionViolations/0"
        return self.get_object(url_suffix, "InspectionViolations")

    def get_permits(self) -> pd.DataFrame:
        url_suffix = "permits/GetOccupancyPermits/0"
        return self.get_object(url_suffix, "OccupancyPermits")

    def get_inspection_categories(self) -> pd.DataFrame:
        url_suffix = "lookups/GetInspectionCategories"
        return self.get_object(url_suffix, "InspectionCategories")

    def get_inspection_types(self) -> pd.DataFrame:
        url_suffix = "lookups/GetInspectionTypes/0"
        return self.get_object(url_suffix, "InspectionTypes")

    def get_violation_code(self) -> pd.DataFrame:
        url_suffix = "inspections/GetViolationCode/0"
        return self.get_object(url_suffix, "ViolationCode")

    def get_permit_status(self) -> pd.DataFrame:
        url_suffix = "lookups/GetPermitStatus/0"
        return self.get_object(url_suffix, "PermitStatusList")

    def create_inspection_report(self, data_file_path, include_historic=False) -> pd.DataFrame:
        inspections = self.get_inspections()

        if not include_historic:
            inspections = inspections.loc[
                inspections["InspectionCompletedDate"] == "0001-01-01T00:00:00"
            ]

        inspections_with_address = self.join_to_occupancies(inspections)

        inspection_types = self.get_inspection_types()
        inspections_with_types = pd.merge(
            inspections_with_address,
            inspection_types,
            on="InspectionTypeId",
            how="left",
        )

        inspection_categories = self.get_inspection_categories()
        inspections_with_categories = pd.merge(
            inspections_with_types,
            inspection_categories,
            left_on="InspectionCategory",
            right_on="OccupancyCategoryId",
            how="left",
        )

        inspections_with_categories.to_csv(data_file_path)

        return inspections_with_categories

    def create_violations_report(self, data_file_path) -> pd.DataFrame:
        violations = self.get_violations()

        violation_codes = self.get_violation_code()
        violations_with_codes = pd.merge(
            violations, violation_codes, on="ViolationCodeId", how="left"
        )

        violations_with_codes.to_csv(data_file_path)
        return violations_with_codes

    def create_permits_report(self, data_file_path, include_historic=False) -> pd.DataFrame:
        permits = self.get_permits()

        if not include_historic:
            two_months_ago = pd.Timestamp.now() - pd.DateOffset(months=2)
            permits = permits.loc[pd.to_datetime(permits["IssuedDate"]) >= two_months_ago]

        permits_with_address = self.join_to_occupancies(permits)

        permit_status = self.get_permit_status()
        permits_with_status = pd.merge(
            permits_with_address, permit_status, on="PermitStatusId", how="left"
        )

        permits_with_status.to_csv(data_file_path)

        return permits_with_status

    # object is inspection or permits dataframe
    def join_to_occupancies(self, object) -> pd.DataFrame:
        # all occupancies from get occupancies endpoint
        existing_occupancies = self.get_occupancies()

        # occupancy ids that are in object (inspection/permit) data but not occupancy endpoinit
        id_difference = list(
            set(object["OccupancyId"]).difference(set(existing_occupancies["OccupancyId"]))
        )

        # loops through all occupancy ids in object data but not occupancies data
        total_loop = len(id_difference)
        loop_start = 1
        updated_occupancies = existing_occupancies
        for occupancy_id in id_difference:
            occupancy = self.get_occupancy(occupancy_id)
            if occupancy["OccupancyId"][0] != "0":
                updated_occupancies = updated_occupancies._append(occupancy, ignore_index=True)
            logging.info(f"Looped through {loop_start} out of {total_loop} occupancies")
            loop_start += 1

        return pd.merge(object, updated_occupancies, on="OccupancyId", how="left")
