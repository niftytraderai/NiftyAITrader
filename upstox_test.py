from upstox_client import Configuration, ApiClient
from upstox_client.api.user_api import UserApi

from config_api import ACCESS_TOKEN

config = Configuration()
config.access_token = ACCESS_TOKEN

client = ApiClient(config)

api = UserApi(client)

response = api.get_profile(api_version="2.0")

print(response)