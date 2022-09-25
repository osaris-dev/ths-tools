import json
import click
import sys
from .ths import THS

# cmd arguments
@click.group()
@click.option('--verbose/--no-verbose', '-v', default=True, help='output debug information')
@click.option('--ths-host', envvar='THS_HOST', default="basic-test.ths.dzhk.med.uni-greifswald.de", help='Enter host name')
@click.option('--ssl-cert', envvar='THS_SSL_CERT', help='name of user certificate (e.g. mmuster.crt)')
@click.option('--ssl-key', envvar='THS_SSL_KEY', help='name of user certificate (e.g. mmuster-decrypted.key)')
@click.option('--bal-user', envvar='THS_BAL_USER', default=None, help='THS BAL username')
@click.option('--bal-pass', envvar='THS_BAL_PASS', default=None, help='BAL password')
@click.option('--ths-api-key', envvar='THS_API_KEY', help='API-Key')
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
def ths_tools_cli(verbose, ssl_cert, ssl_key, ths_host, bal_user, bal_pass, ths_api_key, session_user_id, session_user_name, session_user_title, session_user_firstname, session_user_lastname, session_user_role, token_study_id, token_study_name, token_event, token_reason, token_target_type, patient_identifier_domain):
    global ths
    ths = THS(
        # debug params
        verbose=verbose,

        # connection information
        ths_host=ths_host, 
        ths_api_key=ths_api_key,

        # certificate information
        ssl_cert=ssl_cert, 
        ssl_key=ssl_key,

        # authentication information
        bal_user=bal_user,
        bal_pass=bal_pass,

        # session information
        session_user_id=session_user_id, 
        session_user_name=session_user_name,
        session_user_title=session_user_title,
        session_user_firstname=session_user_firstname,
        session_user_lastname=session_user_lastname,
        session_user_role=session_user_role,

        # token information
        token_study_id=token_study_id,
        token_study_name=token_study_name,
        token_event=token_event,
        token_reason=token_reason, 
        token_target_type=token_target_type,

        # PSN request information
        patient_identifier_domain=patient_identifier_domain
    )

@ths_tools_cli.command()
@click.option('--in-file', type=click.File('r'), default=sys.stdin, help='input file with PSNs')
@click.option('--in-file-type', type=click.Choice(['json', 'text']), default="json", help='input file type')
@click.option('--out-file', type=click.File('w'), default=sys.stdout, help='output file with mapping')
@click.option('--out-file-type', type=click.Choice(['json', 'text']), default="json", help='output file type')
def map_psn_list(in_file, in_file_type, out_file, out_file_type):
    if in_file_type == "json":
        id_list = json.load(in_file)
    elif in_file_type == "text":
        txt_string = in_file.read()

        id_list = txt_string.split("\n")

        for entry in id_list:
            if len(entry) == 0:
                id_list.remove(entry)

    mapping_dict = ths.ths_get_psn_map(id_list)

    if out_file_type == "json":
        json.dump(mapping_dict, out_file, indent=2)
    elif in_file_type == "text":
        for entry in mapping_dict:
            out_file.write(entry + ": " + mapping_dict[entry] + "\n")