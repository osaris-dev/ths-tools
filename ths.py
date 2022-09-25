import requests
from requests.auth import HTTPBasicAuth
import time
import sys

class THS:
    # specify request handling parameters
    max_pseudonyms_per_request = 1000
    retries_before_fail = 5
    wait_after_fail = 3

    def __init__(self, config):
        self.config = config

        if self.config["bal_auth"]:
            self.auth=HTTPBasicAuth(self.config["bal_user"], self.config["bal_pass"])
        else:
            self.auth=None


    def ths_post_request(self,url,json):
        return requests.post(url,
                        cert=(self.config["ssl_cert"], self.config["ssl_key"]),
                        auth=self.auth, verify=True,
                        headers=self.config["header"], json=json)

    def ths_session_request(self):
        # Making a post request
        r = self.ths_post_request(self.config["session_url"], self.config["session_params"])

        if self.config["verbose"]:
            error_print("Session: ")
            error_print("Status Code:", r.status_code)
            #error_print(r.text)
            error_print("------------------------\n")

        session_info = r.json()
        session_id = session_info["sessionId"]

        return session_id


    def ths_token_request(self,session_id):
        path = self.config["session_url"] + session_id + "/tokens"

        # Making a post request
        r = self.ths_post_request(path, self.config["token_params"])

        if self.config["verbose"]:
            error_print("Token: ")
            error_print("Status Code:", r.status_code)
            #error_print(r.text)
            error_print("------------------------\n")

        token_info = r.json()
        token = token_info["tokenId"]

        return token


    def ths_call_request_PSN(self, token, pm, counter):
        path = self.config["psn_request_url"] + token

        # Making a post request
        r = self.ths_post_request(path, pm)

        if self.config["verbose"]:
            error_print("Request PSN:")
            error_print("Status Code:", r.status_code)
            error_print("Iteration number: ", counter+1)
            #error_print(r.text)
            error_print("------------------------\n")
        
        psn_info = r.json()
            
        return [r, psn_info]

    def ths_get_psn_map(self, transfer_id_list):

        # split transfer id list into chunks of 100
        id_list_chunks = [transfer_id_list[x:x + self.max_pseudonyms_per_request] for x in range(0, len(transfer_id_list), self.max_pseudonyms_per_request)]

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
                                "domain": self.config["patient_identifier_domain"],
                                "name": "PSN",
                                "id": id,
                                "type": "patientPSN"
                            }
                        })
                patient_counter += 1

            # define parameters to be passed as json in post request (ths_call_request_PSN)
            pm = {"patients": patients}

            # try request as many times as specified if response does not have a success status code (2xx)
            request_successful = False
            for i in range(self.retries_before_fail):
                session_id = self.ths_session_request()
                token = self.ths_token_request(session_id)
                psn_infos = self.ths_call_request_PSN(token, pm, request_counter)

                i += 1

                if psn_infos[0].status_code not in [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]:
                    # wait specified amount of seconds
                    error_print("Sleep 3 seconds...")
                    time.sleep(self.wait_after_fail)
                    error_print("wake up")

                else:
                    request_successful = True
                    # end loop when status code is 2xx
                    break

            if not request_successful:
                raise Exception(f"Request not successful after {self.retries_before_fail} retries")

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

def zip_dictionaries(dicts):
    # takes list of dictionaries and puts all dictionaries together in one
    from collections import defaultdict

    dd = defaultdict(str)

    for d in dicts:
        for key, value in d.items():
            dd[key] = value
    return dd

def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
