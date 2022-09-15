"""
Copyright 2022 Universitätsklinikum Köln (AöR), Universitätsklinikum Frankfurt: Markus Brechtel, Nils Tulke and Robert Martincevic

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from json import load
import ast
import os


def call_request_PSN(config, pm, counter):
    with open("json/token_info.json") as f:
        token_info = load(f)

    path = config["psn_request_url"] + token_info["tokenId"]

    # Making a post request
    r = requests.post(path, cert=(f'cert/{config["user"]}.crt', f'cert/{config["user"]}-decrypted.key'),
                      auth=HTTPBasicAuth(config["name"], config["login"]), verify=True,
                      headers=config["header"], json=pm)

    print("Request PSN:")
    print("URL:", r.url)
    print("Status Code:", r.status_code)
    print("HTML:\n", r.text)
    print("Iteration number: ", counter+1)
    print("------------------------\n")

    psn_info = r.text

    # convert string to dictionary
    d = ast.literal_eval(psn_info)

    with open(f'patient_acc/psn_info.json', 'w') as f:
        json.dump(d, f, indent=2)

    os.remove("json/token_info.json")

    return r


def main():
    call_request_PSN()


if __name__ == "__main__":
    main()
