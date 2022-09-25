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

import json
import click
import sys
from ths import THS

# cmd arguments
@click.command()
@click.option('--verbose/--no-verbose', '-v', default=True, help='output debug information')
@click.option('--in-file', type=click.File('r'), default=sys.stdin, help='input file with PSNs')
@click.option('--in-file-type', type=click.Choice(['json', 'text']), default="json", help='input file type')
@click.option('--out-file', type=click.File('w'), default=sys.stdout, help='output file with mapping')
@click.option('--out-file-type', type=click.Choice(['json', 'text']), default="json", help='output file type')
@click.option('--host', envvar='THS_HOST', default="basic-test.ths.dzhk.med.uni-greifswald.de", help='Enter host name')
@click.option('--ssl-cert', envvar='THS_SSL_CERT', help='name of user certificate (e.g. mmuster.crt)')
@click.option('--ssl-key', envvar='THS_SSL_KEY', help='name of user certificate (e.g. mmuster-decrypted.key)')
@click.option('--bal-auth/--no-bal-auth', envvar='THS_BAL_AUTH', default=True, help='enable/disable BAL auth')
@click.option('--bal-user', envvar='THS_BAL_USER', help='THS BAL username')
@click.option('--bal-pass', envvar='THS_BAL_PASS', help='BAL password')
@click.option('--api-key', envvar='THS_API_KEY', help='API-Key')
@click.option('--session-user-id', envvar='THS_SESSION_USER_ID', default="test")
@click.option('--session-user-name', envvar='THS_SESSION_USER_NAME', default="test")
@click.option('--session-user-title', envvar='THS_SESSION_USER_TITLE', default="")
@click.option('--session-user-firstname', envvar='THS_SESSION_USER_FIRSTNAME', default="test")
@click.option('--session-user-lastname', envvar='THS_SESSION_USER_LASTNAME', default="test")
@click.option('--session-user-role', envvar='THS_SESSION_USER_ROLE', default="test")
@click.option('--token-study-id', envvar='THS_TOKEN_STUDY_ID', default="noStudy")
@click.option('--token-study_name', envvar='THS_TOKEN_STUDY_NAME', default="noStudy")
@click.option('--token-event', envvar='THS_TOKEN_EVENT', default="acc_temp_merge")
@click.option('--token-reason', envvar='THS_TOKEN_REASON', default="acc_temp_merge")
@click.option('--token-target_type', envvar='THS_TOKEN_TARGET_TYPE', default="accounting")
@click.option('--patient-identifier-domain', envvar='THS_PATIENT_IDENTIFIER_DOMAIN', default="temp")
def main(verbose, host, in_file, in_file_type, out_file, out_file_type, ssl_cert, ssl_key, bal_auth, bal_user, bal_pass, api_key, session_user_id, session_user_name, session_user_title, session_user_firstname, session_user_lastname, session_user_role, token_study_id, token_study_name, token_event, token_reason, token_target_type, patient_identifier_domain):
    
    # initialize config
    ths_config = {
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

    ths = THS(ths_config)

    if in_file_type == "json":
        transfer_id_list = json.load(in_file)
    elif in_file_type == "text":
        transfer_id_list = read_in_file_text(in_file)


    mapping_dict = ths.ths_get_psn_map(transfer_id_list)

    if out_file_type == "json":
        json.dump(mapping_dict, out_file, indent=2)
    elif in_file_type == "text":
        write_out_file_text(mapping_dict, out_file)

def read_in_file_text(in_file):
    # read in transfer IDs from txt file
    txt_string = in_file.read()

    transfer_id_list = txt_string.split("\n")

    for entry in transfer_id_list:
        if len(entry) == 0:
            transfer_id_list.remove(entry)

    return transfer_id_list

def write_out_file_text(mapping_dict, out_file):
    # Alternatively write dictionary to txt file
    for entry in mapping_dict:
        out_file.write(entry + ": " + mapping_dict[entry] + "\n")



if __name__ == "__main__":
    main()
