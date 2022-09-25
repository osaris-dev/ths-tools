Tools for interacting with the API of the Treuhandstelle Greifswald

This package provides a CLI Interface and a Python Class.

# Installation
Install with Pip:
```
pip install git+https://github.com/osaris-dev/ths-tools.git
```

# CLI
Basic usage:
```
ths-tools -v \
    --ssl-cert ths-test.crt --ssl-key ths-test.key \
    --bal-user my_user_name --bal-pass my_password_123 \
    --ths-api-key accounting.test.abc123 \
    map-psn-list --in-file Downloads/test-transfer-ids-20220919.txt --in-file-type text --out-file-type text
```

You can also put the arguments in environment variables, for example with a bash shell you can do:

```
export THS_API_KEY=accounting.test.abc123
export THS_SSL_CERT=ths-test.crt
export THS_SSL_KEY=ths-test.key
export THS_BAL_USER=my_user_name
export THS_BAL_PASS=my_password_123

ths-tools -v map-psn-list --in-file Downloads/test-transfer-ids-20220919.txt --in-file-type text --out-file-type text
```

# Use the Python Class
After installing the Package with Pip you can use the THS class. See example.py.
