import inspect
import upstox_client

print(inspect.signature(
    upstox_client.OptionsApi.get_put_call_option_chain
))