import requests
import logging
import pandas as pd

class Streamline:
    def __init__(self, client_id, client_secret, tenant_id, subscription_key, base_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.subscription_key = subscription_key
        self.base_url = base_url

    def make_api_call(self, method, url, headers, payload=None):
        try:
            if payload:
                response = requests.request(method, url, headers=headers, data=payload)
            else:
                response = requests.request(method, url, headers=headers)

            logging.info(
                "Response: " + str(response.status_code) + ", " + response.reason
            )

            if response.status_code == 200:
                return response

            else:
                logging.error("Api request returned a non-200 response")
                logging.error(response.json())
                raise Exception("Error making api request")

        except:
            raise Exception("Error making api request")


    def getToken(self):
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": f"{self.client_id}/.default"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = self.make_api_call("POST", url, headers, payload)
        logging.info("Successfully got access token")

        return response.json()['access_token']
    
    def get_object(self, token, url_suffix, object_name):
        headers = {
            "Authorization": f"Bearer {token}",
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }
        url = f"{self.base_url}/{url_suffix}"
        response = self.make_api_call("GET", url, headers)

        logging.info(f"Successfully got {object_name}")

        if object_name == 'Occupancy':
            return pd.DataFrame([response.json()])
        else:
            return pd.DataFrame(response.json()[object_name])

    def get_occupancies(self, token):
        url_suffix = "occupancy/GetOccupancies/1/?PageIndex=1&PageCount=4000"
        return self.get_object(token, url_suffix, "Occupancies")
    
    def get_occupancy(self, token, occupancy_id):
        url_suffix = f"occupancy/GetOccupancy/{occupancy_id}"
        return self.get_object(token, url_suffix, "Occupancy")

    def get_inspections(self, token):
        url_suffix = "inspections/GetOccupancyInspections/0"
        return self.get_object(token, url_suffix, 'OccupancyInspection')
    
    def get_violations(self, token):
        url_suffix = "inspections/GetInspectionViolations/0"
        return self.get_object(token, url_suffix, 'InspectionViolations')

    def get_permits(self, token):
        url_suffix = "permits/GetOccupancyPermits/0"
        return self.get_object(token, url_suffix, 'OccupancyPermits')

    def get_inspection_categories(self, token):
        url_suffix = "lookups/GetInspectionCategories"
        return self.get_object(token, url_suffix, "InspectionCategories")
    
    def get_inspection_types(self, token):
        url_suffix = "lookups/GetInspectionTypes/0"
        return self.get_object(token, url_suffix, "InspectionTypes")

    def get_violation_code(self, token):
        url_suffix = "inspections/GetViolationCode/0"
        return self.get_object(token, url_suffix, "ViolationCode")

    def get_permit_status(self, token):
        url_suffix = "lookups/GetPermitStatus/0"
        return self.get_object(token, url_suffix, "PermitStatusList")

    def create_inspection_report(self, token, data_file_path):
        inspections = self.get_inspections(token)

        inspections_with_address = self.join_to_occupancies(token, inspections)

        inspection_types = self.get_inspection_types(token)
        inspections_with_types = pd.merge(inspections_with_address, inspection_types, on='InspectionTypeId', how='left')

        inspection_categories = self.get_inspection_categories(token)
        inspections_with_categories = pd.merge(inspections_with_types, inspection_categories, left_on='InspectionCategory', right_on='OccupancyCategoryId', how='left')

        inspections_with_categories.to_csv(data_file_path)

        return inspections_with_categories
    
    def create_violations_report(self, token, data_file_path):
        violations = self.get_violations(token)

        violation_codes = self.get_violation_code(token)
        violations_with_codes = pd.merge(violations, violation_codes, on='ViolationCodeId', how='left')

        violations_with_codes.to_csv(data_file_path)
        return violations_with_codes
    
    def create_permits_report(self, token, data_file_path):
        permits = self.get_permits(token)

        permits_with_address = self.join_to_occupancies(token, permits)

        permit_status = self.get_permit_status(token)
        permits_with_status = pd.merge(permits_with_address, permit_status, on='PermitStatusId', how='left')

        permits_with_status.to_csv(data_file_path)

        return permits_with_status
    
    # object is inspection or permits dataframe
    def join_to_occupancies(self, token, object):
        # all occupancies that have previously been found in the data
        existing_occupancies = pd.read_csv("streamline_puller/occupancies.csv")

        # occupancy ids that are in object (inspeciton/permit) data but not occupancy data
        id_difference = list(set(object["OccupancyId"]).difference(set(existing_occupancies["OccupancyId"])))

        # loops through all occupancy ids in object data but not occupancies data
        # adds to occupancy data if new occupancy is encountered
        total_loop = len(id_difference)
        loop_start = 1
        updated_occupancies = existing_occupancies
        for occupancy_id in id_difference:
            occupancy = self.get_occupancy(token, occupancy_id)
            if occupancy["OccupancyId"][0] != '0':
                updated_occupancies = updated_occupancies._append(occupancy, ignore_index=True)
            print(f"Looped through {loop_start} out of {total_loop} occupancies")
            loop_start += 1
        
        updated_occupancies.to_csv("streamline_puller/occupancies.csv")

        return pd.merge(object, updated_occupancies, on='OccupancyId', how='left')