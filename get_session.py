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
import ast


def session_request(config):
    # Making a post request
    r = requests.post(config["session_url"],
                      cert=(f'cert/{config["user"]}.crt', f'cert/{config["user"]}-decrypted.key'),
                      auth=HTTPBasicAuth(config["name"], config["login"]), verify=True,
                      headers=config["header"], json=config["session_params"])

    print("Session: ")
    print("URL:", r.url)
    print("Status Code:", r.status_code)
    print("HTML:\n", r.text)
    print("------------------------\n")

    session_info = r.text

    d = ast.literal_eval(session_info)

    with open('json/session_info.json', 'w') as f:
        json.dump(d, f, indent=2)

    return d


def main():
    session_request()


if __name__ == "__main__":
    main()
