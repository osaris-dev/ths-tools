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
from json import dump
import time
import click
from datetime import datetime

# specify request handling parameters
max_pseudonyms_per_request = 100
retries_before_fail = 5
wait_after_fail = 3

transfer_id_length = 36

# cmd arguments
@click.command()
@click.option('--certname', '-c', prompt='certificate name',
              help='name of user certificate (e.g. mmuster.crt, mmuster-decrypted.key -> --certname mmuster)')
@click.option('--baluser', '-bu', prompt='BAL user',
              help='THS BAL username')
@click.option('--balpassword', '-bp', prompt='BAL password', help='BAL password')
@click.option('--apikey', '-ak', prompt='API password', help='Enter API Key')
@click.option('--host', '-h', default="basic-test.ths.dzhk.med.uni-greifswald.de", help='Enter host name')
def cmd_args(certname, baluser, balpassword, apikey, host):
    date = datetime.today().strftime("%Y%m%d")
    # initialize config
    config = {
        "header": {
            "apiKey": apikey,
            "Content-Type": "application/json; charset=utf-8",
            "Host": host
        },
        "session_url": f"https://{host}/dzhk/rest/sessions/",
        "session_params": {
            "data":
                {
                    "fields":
                        {
                            "user_id": "test",
                            "user_name": "test",
                            "user_title": "",
                            "user_firstname": "test",
                            "user_lastname": "test",
                            "user_role": "test"
                        }
                }
        },
        "token_params": {
            "type": "requestPSN",
            "method": "getOrCreate",
            "data":
                {
                    "fields":
                        {
                            "study_id": "noStudy",
                            "study_name": "noStudy",
                            "event": "acc_temp_merge",
                            "reason": "acc_temp_merge",
                            "targetType": "accounting"
                        }
                }
        },
        "psn_request_url": f"https://{host}/dzhk/rest/psn/request/",
        "user_cert": certname,
        "name": baluser,
        "login": balpassword,
        "filename": f"test_transfer_ids/test-transfer-ids-{date}.txt"
    }
    main(config)


def session_request(config):
    # Making a post request
    r = requests.post(config["session_url"],
                      cert=(f'cert/{config["user_cert"]}.crt', f'cert/{config["user_cert"]}-decrypted.key'),
                      auth=HTTPBasicAuth(config["name"], config["login"]), verify=True,
                      headers=config["header"], json=config["session_params"])

    print("Session: ")
    print("Status Code:", r.status_code)
    print("------------------------\n")

    session_info = r.text
    # convert string to dictionary
    d = ast.literal_eval(session_info)
    session_id = d["sessionId"]

    return session_id


def token_request(config, session_id):
    path = config["session_url"] + session_id + "/tokens"

    # Making a post request
    r = requests.post(path, cert=(f'cert/{config["user_cert"]}.crt', f'cert/{config["user_cert"]}-decrypted.key'),
                      auth=HTTPBasicAuth(config["name"], config["login"]), verify=True,
                      headers=config["header"], json=config["token_params"])

    print("Token: ")
    print("Status Code:", r.status_code)
    print("------------------------\n")

    token_info = r.text
    # convert string to dictionary
    d = ast.literal_eval(token_info)
    token = d["tokenId"]

    return token


def call_request_PSN(config, token, pm, counter):
    path = config["psn_request_url"] + token

    # Making a post request
    r = requests.post(path, cert=(f'cert/{config["user_cert"]}.crt', f'cert/{config["user_cert"]}-decrypted.key'),
                      auth=HTTPBasicAuth(config["name"], config["login"]), verify=True,
                      headers=config["header"], json=pm)

    print("Request PSN:")
    print("Status Code:", r.status_code)
    print("Iteration number: ", counter+1)
    print("------------------------\n")

    psn_info = r.text
    # convert string to dictionary
    d = ast.literal_eval(psn_info)

    return [r, d]


def zip_dictionaries(dicts):
    # takes list of dictionaries and puts all dictionaries together in one
    from collections import defaultdict

    dd = defaultdict(str)

    for d in dicts:
        for key, value in d.items():
            dd[key] = value
    return dd


def main(config):
    filename = config["filename"]

    # read in transfer IDs from txt file
    with open(filename, "r") as file:
        txt_string = file.read()

    transfer_id_list = txt_string.split("\n")

    for entry in transfer_id_list:
        if len(entry) != transfer_id_length:
            transfer_id_list.remove(entry)

    # split transfer id list into chunks of 100
    id_list_chunks = [transfer_id_list[x:x + max_pseudonyms_per_request] for x in range(0, len(transfer_id_list), max_pseudonyms_per_request)]

    # list to be filled with dictionaries created from each chunk
    dict_list = []

    request_counter = 0
    patient_counter = 0
    for chunk in id_list_chunks:
        # dictionary to be filled from current chunk of transfer IDs
        mapping_dict_chunk = {}
        # list of patients to be filled for pseudonym request
        patients = []

        for id in chunk:

            patients.append({
                        "index": patient_counter,
                        "patientIdentifier": {
                            "domain": "temp",
                            "name": "PSN",
                            "id": id,
                            "type": "patientPSN"
                        }
                    })
            patient_counter += 1

        # define parameters to be passed as json in post request (call_request_PSN)
        pm = {"patients": patients}

        # try request as many times as specified if response does not have a success status code (2xx)
        request_successful = False
        for i in range(retries_before_fail):
            session_id = session_request(config)
            token = token_request(config, session_id)
            psn_infos = call_request_PSN(config, token, pm, request_counter)

            i += 1

            if psn_infos[0].status_code not in [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]:
                # wait specified amount of seconds
                print("Sleep 3 seconds...")
                time.sleep(wait_after_fail)
                print("wake up")

            else:
                request_successful = True
                # end loop when status code is 2xx
                break

        if not request_successful:
            raise Exception(f"Request not successful after {retries_before_fail} retries")

        # loop through temporary json response file (containing current chunk of patients)
        # mapping transfer IDs to target IDs
        for patient in psn_infos[1]["patients"]:
            pat_identifier = patient["patientIdentifier"]["id"]
            target_id = patient["targetId"]
            mapping_dict_chunk[pat_identifier] = target_id

        # append dictionary created out of current chunk to dictionary list
        dict_list.append(mapping_dict_chunk)

        request_counter += 1

    # create overall mapping dictionary
    mapping_dict = zip_dictionaries(dict_list)

    # write dictionary to json file
    with open("patient_acc/mapping_test.json", "w") as j:
        dump(mapping_dict, j, indent=2)

    """
    # Alternatively write dictionary to txt file
    path = "patient_acc/psn_mapping.txt"
    with open(path, 'w') as f:
        for entry in mapping_dict:
            f.write(entry + ": " + mapping_dict[entry] + "\n")
    """


if __name__ == "__main__":
    cmd_args()
