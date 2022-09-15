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
import ast
import json
from json import load
import os


def token_request(config):
    with open("json/session_info.json") as f:
        session_info = load(f)

    path = config["session_url"] + session_info[
        "sessionId"] + "/tokens"

    # Making a post request
    r = requests.post(path, cert=(f'cert/{config["user"]}.crt', f'cert/{config["user"]}-decrypted.key'),
                      auth=HTTPBasicAuth(config["name"], config["login"]), verify=True,
                      headers=config["header"], json=config["token_params"])

    print("Token: ")
    print("URL:", r.url)
    print("Status Code:", r.status_code)
    print("HTML:\n", r.text)
    print("------------------------\n")

    token_info = r.text

    d = ast.literal_eval(token_info)

    with open('json/token_info.json', 'w') as f:
        json.dump(d, f, indent=2)

    os.remove("json/session_info.json")

    return d


def main():
    token_request()


if __name__ == "__main__":
    main()
