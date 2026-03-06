# Creating profiles

> ⚠️ Inside of `.gitignore` file, there is a policy to ignore every file with `.yaml` extension inside this path. Keep this in mind to avoid any undesired credential sharing!

## Create a profile file for each environment

Follow this pattern:

- File name: <env_name>.yaml
- Content as bellow:

``` YAML
name: <env_name>

zabbix:
  url: <zabbix_url>/api_jsonrpc.php
  username: <api_user_name>
  password: <api_password>
```

## For example: itguy.yaml
``` YAML
name: itguy

zabbix:
  url: http://itguy.domain/zabbix/api_jsonrpc.php
  username: john.doe
  password: 123_changeAsSo0n4sP0ss1bl3
```