import requests
from requests.auth import HTTPBasicAuth
import time
import sys

class THS:
    # specify request handling parameters
    max_pseudonyms_per_request = 1000
    retries_before_fail = 5
    wait_after_fail = 3

    def __init__(self, ths_host, ths_api_key, ssl_cert, ssl_key, session_user_id, session_user_name, session_user_title, session_user_firstname, session_user_lastname, session_user_role, token_study_id, token_study_name, token_event, token_reason, token_target_type, patient_identifier_domain, https_proxy_url=False, bal_user=False, bal_pass=False, verbose=False, accept_missing_target_id=False):

        self.verbose = verbose

        if bal_user and bal_pass:
            self.auth=HTTPBasicAuth(bal_user, bal_pass)
        else:
            self.auth=None

        self.cert = (ssl_cert, ssl_key)

        self.header =  {
            "apiKey": ths_api_key,
            "Content-Type": "application/json; charset=utf-8",
        }

        self.ths_host = ths_host

        if https_proxy_url:
            self.proxies = {
                 'https': https_proxy_url
            }
        else:
            self.proxies = None

        self.session_url = f"https://{ths_host}/dzhk/rest/sessions/"
        self.session_params = {
            "data":
                {
                    "fields":
                        {
                            "user_id": session_user_id,
                            "user_name": session_user_name,
                        }
                }
        }
        if session_user_title:
            self.session_params['data']['fields']['user_title'] = session_user_title
        if session_user_firstname:
            self.session_params['data']['fields']['user_firstname'] = session_user_firstname
        if session_user_lastname:
            self.session_params['data']['fields']['user_lastname'] = session_user_lastname
        if session_user_role:
            self.session_params['data']['fields']['user_role'] = session_user_role

        self.token_params = {
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
        }

        self.psn_request_url = f"https://{ths_host}/dzhk/rest/psn/request/"
        self.patient_identifier_domain = patient_identifier_domain

        self.accept_missing_target_id = accept_missing_target_id

    def ths_post_request(self,url,json):
        return requests.post(url,
                        cert=self.cert,
                        auth=self.auth, verify=True,
                        headers=self.header, json=json, proxies=self.proxies)

    def ths_session_request(self):
        # Making a post request
        r = self.ths_post_request(self.session_url, self.session_params)
        if self.verbose:
            error_print("THS Session Request:", r, r.text)
            error_print("------------------------\n")

        if r.status_code != 201:
            raise Exception(f"THS Session Request: Invalid response from server: {r} {r.text}")

        session_info = r.json()


        session_id = session_info["sessionId"]

        return session_id


    def ths_token_request(self,session_id):
        path = self.session_url + session_id + "/tokens"

        # Making a post request
        r = self.ths_post_request(path, self.token_params)

        if self.verbose:
            error_print("THS Token Request:", r, r.text)
            error_print("------------------------\n")

        if r.status_code != 201:
            raise Exception(f"THS Token Request: Invalid response from server: {r} {r.text}")

        token_info = r.json()
        token = token_info["tokenId"]

        return token


    def ths_call_request_PSN(self, token, pm, counter):
        path = self.psn_request_url + token

        # Making a post request
        r = self.ths_post_request(path, pm)

        if self.verbose:
            error_print("Request PSN:", counter, r, r.text )
            error_print("------------------------\n")

        return r

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
                                "domain": self.patient_identifier_domain,
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

                if psn_infos.status_code not in [200, 201, 202, 203, 204, 205, 206, 207, 208, 226]:
                    # wait specified amount of seconds
                    error_print("Sleep 3 seconds...")
                    time.sleep(self.wait_after_fail)
                    error_print("wake up")

                else:
                    request_successful = True
                    # end loop when status code is 2xx
                    break

            if not request_successful:
                raise Exception(f"Request not successful after {self.retries_before_fail} retries. Last response: {psn_infos} {psn_infos.text}")

            try:
                psn_infos_json = psn_infos.json()
            except:
                raise Exception(f"THS Get PSN Map: Could not deserialize JSON. Got response: {psn_infos} {psn_infos.text} ")


            # loop through temporary json response file (containing current chunk of patients)
            # mapping transfer IDs to target IDs
            for patient in psn_infos_json["patients"]:

                if self.accept_missing_target_id:
                    pat_identifier = patient["patientIdentifier"]["id"]
                    if 'targetId' in patient:
                        target_id = patient["targetId"]
                        mapping_dict_chunk[pat_identifier] = target_id
                    else:
                        mapping_dict_chunk[pat_identifier] = None
                else:
                    try:
                        psn_info_json = psn_infos.json()
                        for patient in psn_info_json["patients"]:
                            pat_identifier = patient["patientIdentifier"]["id"]
                            target_id = patient["targetId"]
                            mapping_dict_chunk[pat_identifier] = target_id
                    except:
                        raise Exception(f"THS Get PSN Map: Could not unpack patient targetId. Got response: {psn_infos} {psn_infos.text} ")

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
