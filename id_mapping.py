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
@click.option('--verbose/--no-verbose', '-v', default=True, help='output debug information')
@click.option('--in-file', type=click.Path(exists=True), help='input file with PSNs')
@click.option('--in-file-type', type=click.Choice(['json', 'text']), default="json", help='input file type')
@click.option('--out-file', type=click.Path(), help='output file with mapping')
@click.option('--out-file-type', type=click.Choice(['json', 'text']), default="json", help='output file type')
@click.option('--host', default="basic-test.ths.dzhk.med.uni-greifswald.de", help='Enter host name')
@click.option('--ssl-cert', help='name of user certificate (e.g. mmuster.crt)')
@click.option('--ssl-key', help='name of user certificate (e.g. mmuster-decrypted.key)')
@click.option('--bal-auth/--no-bal-auth', default=True, help='enable/disable BAL auth')
@click.option('--bal-user', help='THS BAL username')
@click.option('--bal-pass', help='BAL password')
@click.option('--api-key', help='API-Key')
@click.option('--session-user-id', default="test")
@click.option('--session-user-name', default="test")
@click.option('--session-user-title', default="")
@click.option('--session-user-firstname', default="test")
@click.option('--session-user-lastname', default="test")
@click.option('--session-user-role', default="test")
@click.option('--token-study-id', default="noStudy")
@click.option('--token-study_name', default="noStudy")
@click.option('--token-event', default="acc_temp_merge")
@click.option('--token-reason', default="acc_temp_merge")
@click.option('--token-target_type', default="accounting")
@click.option('--patient-identifier-domain', default="temp", help='output debug information')
def main(verbose, host, in_file, in_file_type, out_file, out_file_type, ssl_cert, ssl_key, bal_auth, bal_user, bal_pass, api_key, session_user_id, session_user_name, session_user_title, session_user_firstname, session_user_lastname, session_user_role, token_study_id, token_study_name, token_event, token_reason, token_target_type, patient_identifier_domain):
    
    # initialize config
    config = {
        "header": {
            "apiKey": api_key,
            "Content-Type": "application/json; charset=utf-8",
            "Host": host
        },
        "session_url": f"https://{host}/dzhk/rest/sessions/",
        "session_params": {
            "data":
                {
                    "fields":
                        {
                            "user_id": session_user_id,
                            "user_name": session_user_name,
                            "user_title": session_user_title,
                            "user_firstname": session_user_firstname,
                            "user_lastname": session_user_lastname,
                            "user_role": session_user_role
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
                            "study_id": token_study_id,
                            "study_name": token_study_name,
                            "event": token_event,
                            "reason": token_reason,
                            "targetType": token_target_type
                        }
                }
        },
        "psn_request_url": f"https://{host}/dzhk/rest/psn/request/",
        "bal_auth": bal_auth,
        "bal_user": bal_user,
        "bal_pass": bal_pass,
        "ssl_cert": ssl_cert,
        "ssl_key": ssl_key,
        "verbose": verbose,
        "patient_identifier_domain": patient_identifier_domain,
    }

    if in_file_type == "json":
        transfer_id_list = read_in_file_json(in_file)
    elif in_file_type == "text":
        transfer_id_list = read_in_file_text(in_file)

    mapping_dict = get_psn_map(transfer_id_list,config)

    if out_file_type == "json":
        write_out_file_json(mapping_dict, out_file)
    elif in_file_type == "text":
        write_out_file_text(mapping_dict, out_file)

    

def ths_post_request(url,json,config):
    if config["bal_auth"]:
        auth=HTTPBasicAuth(config["bal_user"], config["bal_pass"])
    else:
        auth=None
    return requests.post(url,
                      cert=(config["ssl_cert"], config["ssl_key"]),
                      auth=auth, verify=True,
                      headers=config["header"], json=json)

def session_request(config):
    # Making a post request
    r = ths_post_request(config["session_url"],config["session_params"],config)

    if config["verbose"]:
        print("Session: ")
        print("Status Code:", r.status_code)
        print("------------------------\n")

    session_info = r.json()
    session_id = session_info["sessionId"]

    return session_id


def token_request(config, session_id):
    path = config["session_url"] + session_id + "/tokens"

    # Making a post request
    r = ths_post_request(path, config["token_params"], config)

    if config["verbose"]:
        print("Token: ")
        print("Status Code:", r.status_code)
        print("------------------------\n")

    token_info = r.json()
    token = token_info["tokenId"]

    return token


def call_request_PSN(config, token, pm, counter):
    path = config["psn_request_url"] + token

    # Making a post request
    r = ths_post_request(path, pm, config)

    if config["verbose"]:
        print("Request PSN:")
        print("Status Code:", r.status_code)
        print("Iteration number: ", counter+1)
        print("------------------------\n")

    psn_info = r.json()
    return [r, psn_info]


def zip_dictionaries(dicts):
    # takes list of dictionaries and puts all dictionaries together in one
    from collections import defaultdict

    dd = defaultdict(str)

    for d in dicts:
        for key, value in d.items():
            dd[key] = value
    return dd


def read_in_file_text(in_file):
    # read in transfer IDs from txt file
    with open(in_file, "r") as file:
        txt_string = file.read()

    transfer_id_list = txt_string.split("\n")

    for entry in transfer_id_list:
        if len(entry) != transfer_id_length:
            transfer_id_list.remove(entry)

    return transfer_id_list

def read_in_file_json(in_file):
    # read in transfer IDs from txt file
    with open(in_file, "r") as file:
        return json.load(file)

def get_psn_map(transfer_id_list, config):

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
                            "domain": config["patient_identifier_domain"],
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
    return zip_dictionaries(dict_list)

def write_out_file_json(mapping_dict, out_file):
    # write dictionary to json file
    with open(out_file, "w") as j:
        json.dump(mapping_dict, j, indent=2)

def write_out_file_text(mapping_dict, out_file):
    # Alternatively write dictionary to txt file
    with open(out_file, 'w') as f:
        for entry in mapping_dict:
            f.write(entry + ": " + mapping_dict[entry] + "\n")

if __name__ == "__main__":
    main()
