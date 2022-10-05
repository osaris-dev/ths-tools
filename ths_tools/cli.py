import json
import click
import sys
from .ths import THS

# import version info
try:
    from ._version import version as __version__ # type: ignore
except ImportError or ModuleNotFoundError:
    __version__ = "dev"


# cmd arguments
@click.group()
@click.version_option(__version__)
@click.option('--verbose/--no-verbose', '-v', default=False, help='output debug information')
@click.option('--ths-host', envvar='THS_HOST', required=True, help='THS host name')
@click.option('--ssl-cert', envvar='THS_SSL_CERT', required=True, help='name of user certificate (e.g. mmuster.crt)')
@click.option('--ssl-key', envvar='THS_SSL_KEY', required=True, help='name of user certificate (e.g. mmuster-decrypted.key)')
@click.option('--bal-user', envvar='THS_BAL_USER', default=None, help='THS BAL username')
@click.option('--bal-pass', envvar='THS_BAL_PASS', default=None, help='BAL password')
@click.option('--ths-api-key', envvar='THS_API_KEY', required=True, help='API-Key')
@click.option('--session-user-id', envvar='THS_SESSION_USER_ID', required=True)
@click.option('--session-user-name', envvar='THS_SESSION_USER_NAME', required=True)
@click.option('--session-user-title', envvar='THS_SESSION_USER_TITLE')
@click.option('--session-user-firstname', envvar='THS_SESSION_USER_FIRSTNAME')
@click.option('--session-user-lastname', envvar='THS_SESSION_USER_LASTNAME')
@click.option('--session-user-role', envvar='THS_SESSION_USER_ROLE')
@click.option('--token-study-id', envvar='THS_TOKEN_STUDY_ID', required=True)
@click.option('--token-study_name', envvar='THS_TOKEN_STUDY_NAME', required=True)
@click.option('--token-event', envvar='THS_TOKEN_EVENT', required=True)
@click.option('--token-reason', envvar='THS_TOKEN_REASON', required=True)
@click.option('--token-target_type', envvar='THS_TOKEN_TARGET_TYPE', required=True)
@click.option('--patient-identifier-domain', envvar='THS_PATIENT_IDENTIFIER_DOMAIN', required=True)
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
def test_auth():
    print("Testing connection with THS Host:", ths.ths_host)
    session_id = ths.ths_session_request()
    print("Got THS Session ID:",session_id)
    token = ths.ths_token_request(session_id)
    print("Got THS Token ID:",token)

@ths_tools_cli.command()
@click.option('--in-file', type=click.File('r'), default=sys.stdin, help='input file with PSNs')
@click.option('--in-file-type', type=click.Choice(['json', 'text']), default="json", help='input file type')
@click.option('--out-file', type=click.File('w'), default=sys.stdout, help='output file with mapping')
@click.option('--out-file-type', type=click.Choice(['json', 'text']), default="json", help='output file type')
def map_psn_list(in_file, in_file_type, out_file, out_file_type):
    if in_file_type == "json":
        id_list = json.load(in_file)
    elif in_file_type == "text":
        id_list = in_file.read().splitlines() 

        for entry in id_list:
            if len(entry) == 0:
                id_list.remove(entry)

    mapping_dict = ths.ths_get_psn_map(id_list)

    if out_file_type == "json":
        json.dump(mapping_dict, out_file, indent=2)
    elif in_file_type == "text":
        for entry in mapping_dict:
            out_file.write(entry + ": " + mapping_dict[entry] + "\n")

@ths_tools_cli.command()
@click.option('--in-file', type=click.Path(), help='input file with PSNs')
@click.option('--in-file-type', type=click.Choice(['json', 'csv', 'xlsx']), help='input file type')
@click.option('--in-file-json-orient', default="records", help='input file json structure (pandas orient flag)')
@click.option('--in-file-csv-encoding', default=None, help='input file type')
@click.option('--in-file-csv-sep', default=",", help='input file CSV seperator')
@click.option('--out-file', type=click.Path(), help='output file with mapping')
@click.option('--out-file-type', type=click.Choice(['json', 'csv', 'xlsx']), default="json", help='output file type')
@click.option('--out-file-json-orient', default="records", help='output file json structure (pandas orient flag)')
@click.option('--out-file-csv-encoding', default=None, help='output file type')
@click.option('--out-file-csv-sep', default=",", help='output file CSV seperator')
@click.option('--source-psn-column', help='column with PSNs to map')
@click.option('--target-psn-column', help='new column with mapped PSNs ')
@click.option('--drop-source-psn-column/--no-drop-source-psn-column', default=True, help='drop column with PSNs to map (if they are not identical)')
def table_psn_mapper(in_file, in_file_type, in_file_json_orient, in_file_csv_encoding, in_file_csv_sep, out_file, out_file_type, out_file_json_orient, out_file_csv_encoding, out_file_csv_sep, source_psn_column, target_psn_column, drop_source_psn_column):

    import pandas

    if in_file_type == "json":
        table = pandas.read_json(in_file,orient=in_file_json_orient)
    elif in_file_type == "csv":
        table = pandas.read_table(in_file,encoding=in_file_csv_encoding,sep=in_file_csv_sep)
    elif in_file_type == "xlsx":
        table = pandas.read_excel(in_file)
    else:
        raise Exception(f"No valid input file type has been specified!")

    id_list = table[source_psn_column].unique()
    mapping_dict = ths.ths_get_psn_map(id_list)
    table[target_psn_column] = table.apply(lambda x: mapping_dict[x[source_psn_column]],axis=1)

    if drop_source_psn_column and target_psn_column != source_psn_column:
        table = table.drop(columns=[source_psn_column])

    if out_file_type == "json":
        table.to_json(out_file,orient=out_file_json_orient)
    elif out_file_type == "csv":
        table.to_csv(out_file,encoding=out_file_csv_encoding,sep=out_file_csv_sep)
    elif out_file_type == "xlsx":
        table.to_excel(out_file)
    else:
        raise Exception(f"No valid output file type has been specified!")
