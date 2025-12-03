import os
import ldclient
from ldclient import Context
from ldclient.config import Config
from typing import Optional


class LaunchDarklyClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LaunchDarklyClient, cls).__new__(cls)
        return cls._instance

    def initialize(self, sdk_key: Optional[str] = None):
        if self._client is None:
            key = sdk_key or os.getenv('LAUNCHDARKLY_SDK_KEY')
            ldclient.set_config(Config(key))
            self._client = ldclient.get()

            if not self._client.is_initialized():
                raise Exception('LaunchDarkly SDK failed to initialize')

            print('LaunchDarkly SDK successfully initialized')

    def get_client(self):
        if self._client is None:
            self.initialize()
        return self._client

    def create_context(self, user_id: str, email: Optional[str] = None, custom_attributes: Optional[dict] = None):
        builder = Context.builder(user_id).kind('user')

        if email:
            builder.set('email', email)

        if custom_attributes:
            for key, value in custom_attributes.items():
                builder.set(key, value)

        return builder.build()

    def get_flag(self, flag_key: str, context: Context, default_value: bool = False) -> bool:
        client = self.get_client()
        return client.variation(flag_key, context, default_value)

    def close(self):
        if self._client:
            self._client.close()
            self._client = None


ld_client = LaunchDarklyClient()
