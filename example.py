from ths_tools import THS

def main():

    ths = THS(
        verbose=True,

        # connection information
        ths_host="basic-test.ths.dzhk.med.uni-greifswald.de",
        ths_api_key="accounting.test.abc123",

        # certificate information
        ssl_cert="ths-test.crt",
        ssl_key="ths-test.key",

        # authentication information
        bal_user="my_user_name",
        bal_pass="my_password_123",

        # session information
        session_user_id="test",
        session_user_name="test",
        session_user_title="",
        session_user_firstname="test",
        session_user_lastname="test",
        session_user_role="test",

        # token information
        token_study_id="noStudy",
        token_study_name="noStudy",
        token_event="acc_temp_merge",
        token_reason="acc_temp_merge",
        token_target_type="accounting",

        # PSN id information
        patient_identifier_domain="temp"

    )

    with open("Downloads/test-transfer-ids-20220919.txt","r") as in_file:
        transfer_id_list = in_file.read().split("\n")

    for entry in transfer_id_list:
        if len(entry) == 0:
            transfer_id_list.remove(entry)

    mapping_dict = ths.ths_get_psn_map(transfer_id_list)

    with open("Downloads/test-map-ids-20220919.txt","w") as out_file:
        for entry in mapping_dict:
            out_file.write(entry + ": " + mapping_dict[entry] + "\n")

if __name__ == "__main__":
    main()
