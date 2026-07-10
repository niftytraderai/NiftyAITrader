# sdk_check.py

import upstox_client

for item in dir(upstox_client):
    if "Option" in item or "option" in item:
        print(item)