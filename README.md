Tools for interacting with the API of the Treuhandstelle Greifswald

This package provides a CLI Interface and a Python Class.

# Installation
Install with Pip:
```
pip install git+https://github.com/osaris-dev/ths-tools.git
```

# CLI
The CLI has multiple commands:
- test-auth: tests if the client authenticates correctly to the THS Server
- map-psn-list: takes a list of PSNs and retrieves a map of these to the target PSNs
- table-psn-mapper: takes a table and maps a source PSN column to a target PSN column

The --bal-user and --bal-pass options are optional, they are only required if authentication is done via Basic Auth.

Basic usage:
```
ths-tools -v \
    --ths-host test.ths.dzhk.med.uni-greifswald.de \
    --ssl-cert ths-test.crt --ssl-key ths-test.key \
    --bal-user my_user_name --bal-pass my_password_123 \
    --ths-api-key accounting.test.abc123 \
    --session-user-id test \
    --session-user-name test \
    --session-user-title "" \
    --session-user-firstname test \
    --session-user-lastname test \
    --session-user-role test \
    --token-study-id noStudy \
    --token-study_name noStudy \
    --token-event acc_temp_merge \
    --token-reason acc_temp_merge \
    --token-target_type accounting \
    --patient-identifier-domain temp \
    map-psn-list --in-file Downloads/test-transfer-ids-20220919.txt --in-file-type text --out-file-type text
```

You can also put the arguments in environment variables, for example with a bash shell you can do:

```
export THS_HOST=test.ths.dzhk.med.uni-greifswald.de
export THS_API_KEY=accounting.test.abc123
export THS_SSL_CERT=ths-test.crt
export THS_SSL_KEY=ths-test.key
#export THS_BAL_USER=my_user_name
#export THS_BAL_PASS=my_password_123
export THS_SESSION_USER_ID=test
export THS_SESSION_USER_NAME=test
export THS_SESSION_USER_TITLE=""
export THS_SESSION_USER_FIRSTNAME=test
export THS_SESSION_USER_LASTNAME=test
export THS_SESSION_USER_ROLE=test
export THS_TOKEN_STUDY_ID=noStudy
export THS_TOKEN_STUDY_NAME=noStudy
export THS_TOKEN_EVENT=acc_temp_merge
export THS_TOKEN_REASON=acc_temp_merge
export THS_TOKEN_TARGET_TYPE=accounting
export THS_PATIENT_IDENTIFIER_DOMAIN=temp

ths-tools -v map-psn-list --in-file Downloads/test-transfer-ids-20220919.txt --in-file-type text --out-file-type text
```

# Use the Python Class
After installing the Package with Pip you can use the THS class. See example.py.
