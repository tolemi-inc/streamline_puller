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
        data_file_path,
        version="v1",  # Default to v1 for backward compatibility
        username=None,
        password=None,
    ):
        self.version = version  # Set version first so property is available
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.subscription_key = subscription_key
        self.report_name = report_name
        self.include_historical_data = include_historical_data
        self.data_file_path = data_file_path
        self.username = username
        self.password = password

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
        if value is None and self.version == "v1":
            raise ConfigError("Missing client secret in config.")
        else:
            self._client_secret = value

    @property
    def tenant_id(self):
        return self._tenant_id

    @tenant_id.setter
    def tenant_id(self, value):
        if value is None and self.version == "v1":
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
        allowed_values = ["Inspections", "Violations", "Permits", "Occupancies"]
        if value is None:
            raise ConfigError("Missing report name in config")
        elif value in allowed_values:
            self._report_name = value
        else:
            raise ConfigError(
                "Invalid report name: {}. Expecting one of {}".format(
                    value, ", ".join(allowed_values)
                )
            )

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

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if value not in ["v1", "v2"]:
            raise ConfigError("Version must be either 'v1' or 'v2'")
        self._version = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value
