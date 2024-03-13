from config_error import ConfigError

class Config:
    def __init__(
        self,
        client_id,
        client_secret,
        tenant_id,
        subscription_key,
        report_name,
        include_historical_data,
        data_file_path
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.subscription_key = subscription_key
        self.report_name = report_name
        self.include_historical_data = include_historical_data
        self.data_file_path = data_file_path

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        if value is None:
            raise ConfigError("Missing client id in config.")
        else:
            self._client_id = value

    @property
    def client_secret(self):
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value):
        if value is None:
            raise ConfigError("Missing client secret in config.")
        else:
            self._client_secret = value

    @property
    def tenant_id(self):
        return self._tenant_id

    @tenant_id.setter
    def tenant_id(self, value):
        if value is None:
            raise ConfigError("Missing tenant id in config.")
        else:
            self._tenant_id = value

    @property
    def subscription_key(self):
        return self._subscription_key

    @subscription_key.setter
    def subscription_key(self, value):
        if value is None:
            raise ConfigError("Missing subscription key in config.")
        else:
            self._subscription_key = value

    @property
    def report_name(self):
        return self._report_name

    @report_name.setter
    def report_name(self, value):
        allowed_values = ["Inspections", "Violations", "Permits"]
        if value is None:
            raise ConfigError("Missing report name in config")
        elif value in allowed_values:
            self._report_name = value            
        else:
            raise ConfigError("Invalid report name: {}. Expecting one of {}".format(
                value, ", ".join(allowed_values)))
    
    @property
    def include_historical_data(self):
        return self._include_historical_data

    @include_historical_data.setter
    def include_historical_data(self, value):
        if value is None:
            raise ConfigError("Missing include historical data flag in config")
        else:
            self._include_historical_data = value
    
    @property
    def data_file_path(self):
        return self._data_file_path

    @data_file_path.setter
    def data_file_path(self, value):
        if value is None:
            raise ConfigError("Missing data file path in config")
        else:
            self._data_file_path = value