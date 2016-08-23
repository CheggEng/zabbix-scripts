# zabbix-scripts
This is a collection of python scripts created by Chegg Inc to aide in our infrastructure monitoring.

Table of Contents
=================

  * [zabbix-scripts](#zabbix-scripts)
    * [check_s3_file.py](#check_s3_filepy)
      * [Arguments](#arguments)
    * [zabbixMaintenance.py](#zabbixmaintenancepy)
      * [Arguments](#arguments-1)
      * [Disable Example](#disable-example)
      * [Maintence Mode](#maintence-mode)
      * [Delete](#delete)
      * [Create](#create)
    * [zabbix.template.export.py](#zabbixtemplateexportpy)
      * [Arguments](#arguments-2)
    * [License](#license)


## check_s3_file.py
This is a tool to check files in AWS S3.  You can use it to check Age, contents, existence. Returns "FOUND-OK" if everything is fine.  Gives error with reason otherwise. Requires python boto. (sudo pip install boto). This check should work with both Nagios and Zabbix

Requires: 

* [https://github.com/boto/boto](https://github.com/boto/boto) ```pip install boto``` 

### Arguments

```
example-host user$ ./check_s3_file.py --help
usage: check_s3_file.py [-h] --url URL [--regex REGEX] [--ttl TTL]
                        [--access_key ACCESS_KEY] [--secret_key SECRET_KEY]
                        [--aws_profile AWS_PROFILE] [--debug]

optional arguments:
  -h, --help                  Show this help message and exit
  --url URL                   Path to s3 file (ex: s3://zabbix-ops/monitors/check_special_job_output.txt)
  --regex REGEX               Simple regex to apply to file contents
  --ttl TTL                   File age in seconds
  --access_key ACCESS_KEY     AWS Access key ID
  --secret_key SECRET_KEY     AWS Secret Password
  --aws_profile AWS_PROFILE   AWS profile to use from ~/.aws/credentials file
  --debug                     Enable debug mode, this will show you all the json-rpc calls and responses.
```






## zabbixMaintenance.py
This is a tool for modifying hosts (or multiple host contained in a hostgroup).  It has the ability to disable, enable, place in maintenance mode, end a maintenance mode or even delete host(s).

Requires: 

* [https://github.com/blacked/py-zabbix](https://github.com/blacked/py-zabbix) ```pip install py-zabbix``` 


### Arguments

```
example-host user$ ./zabbixMaintenance.py -h
usage: zabbixMaintenance.py [-h] [--hostname HOSTNAME] [--asset-tag ASSET_TAG]
                            [--hostgroup HOSTGROUP] [--delete] [--create]
                            [--ip IP] [--port PORT] [--templates TEMPLATES]
                            [--groups GROUPS] [--enable] [--disable]
                            [--maintenance] [--maintenance-length]
                            [--end-maintenance] [--debug] --url URL --user
                            USER --password PASSWORD

This is a tool for modifying hosts (or multiple host contained in a
hostgroup). It has the ability to disable, enable, place in maintenance mode,
end a maintenance mode or even delete host(s).

optional arguments:
  -h, --help              show this help message and exit
  --hostname HOSTNAME     Hostname to modify
  --asset-tag ASSET_TAG   Find host by asset tag instead of hostname
  --hostgroup HOSTGROUP   Hostgroup to modify
  --delete                Flag that indicates we want to delete the host in question
  --create                Flag that indicates we want to create the host in zabbix
    --ip IP               Specify the ip for a host when creating a new host in zabbix
    --port PORT           Specify the zabbix agent port for a host when creating a new host in zabbix. (default: 10050)
    --templates TEMPLATES Add the following comma separated templates to a host, used when creating a new host.
    --groups GROUPS       Add the following comma separated groups to a host, used when creating a new host
  --enable                Flag that indicates we want to enable the host in question
  --disable               Flag that indicates we want to disable the host in question
  --maintenance           Flag that indicates we want to place the host in maintenance mode
  --maintenance-length    How long in seconds to be in maintenance mode. (default: 3600)
  --end-maintenance       Flag that indicates we want to disable maintenance mode
  --debug                 Enable debug mode, this will show you all the json-rpc calls and responses
  --url URL               URL to the zabbix server (example: https://monitor.example.com/zabbix)
  --user USER             The zabbix api user
  --password PASSWORD     The zabbix api password
```

### Disable Example
This is helpful if you are gonna need to shutdown a host or a group of hosts for a while and don't want to zabbix keep monitoring the hosts.  Replace ```--disable``` with ```--enable``` when you want to bring the host(s) back online.

```
example-host user$ ./zabbixMaintenance.py --url https://monitor.example.com/zabbix --user jdoe --password='secret123' --hostname='web01.example.com' --disable
```

If you give a --hostgroup instead of a hostname, it will find all hosts in the hostgroup and disable each host

```
example-host user$ ./zabbixMaintenance.py --url https://monitor.example.com/zabbix --user jdoe --password='secret123' --hostgroup='webservers' --disable
```

### Maintence Mode
If you are deploying code and need to place host(s) in maintenance mode you can use the ```--maintenance``` flag.  If you've configured your alert actions to have the normal condition of ```Maintenance status not in maintenance``` then no alerts will be sent while in maintenance mode.  By default the maintenance window is one hour (3600) seconds.  You can customize this time with the ```--maintenance-length``` flag.  This is a very helpful script to add to your jenkins deployment scripts.


```
example-host user$ ./zabbixMaintenance.py --url https://monitor.example.com/zabbix --user jdoe --password='secret123' --hostgroup='webservers' --maintenance
```

When you are done with your deployment you can either let the maintenance window expire or you can use the ```--end-maintenance``` flag to to update the end time of the maintenance window to the current time effectively ending the maintenance window.

### Delete
This is helpful if you need to remove zabbix hosts when you terminate the hosts.  Perhaps as a hook in your cloudtrail host clean up processes or in your unit test that may create hosts as part of their test.


```
example-host user$ ./zabbixMaintenance.py --url https://monitor.example.com/zabbix --user jdoe --password='secret123' --hostname='web-sd8dcs2c.example.com' --delete
```

### Create
If you need to define a new host in the zabbix server you can use the ```--create``` flag to create a new host entry in zabbix.  It accepts optional ```--templates``` & ```--groups``` flags to specify templates and groups to assign the host to.  The templates and groups should be comma separated.  Also be sure to include the ```--ip``` argument with the host IP address.

```
example-host user$ ./zabbixMaintenance.py --url https://monitor.example.com/zabbix --user jdoe --password='secret123' --hostname='web-sd8dcs2c.example.com' --ip 10.2.3.4 --templates=Linux,aws --groups=ops  --create
```



## zabbix.template.export.py
This is a simple tool to export zabbix templates for backup. Please note it will always set the date on export to 1/1/2016 so git wont update unless something substantial happens.  Please note that due to a [known bug in Zabbix](https://support.zabbix.com/browse/ZBXNEXT-178) it does not currently backup Web scenarios.  This has supposedly been patched in pre-3.1.0 (trunk).

Using this script you could potentialy automate backing up Zabbix templates. Here's a basic example of the process.

```
#!/bin/bash

cd /var/lib/zabbix/backup
./zabbix.template.export.py --url https://monitor.example.com/zabbix \
	--user='zabbix-api-user' \
	--password='super-secret' \
	--out-dir zabbix-tempaltes
	
cd zabbix-tempaltes
git add .
git commit -am 'automated template backup'
```

### Arguments

```
example-host user$ ./zabbix.template.export.py  --help
usage: zabbix.template.export.py [-h] [--templates TEMPLATES]
                                 [--out-dir OUT_DIR] [--debug] --url URL
                                 --user USER --password PASSWORD

optional arguments:
  -h, --help                  Show this help message and exit
  --templates TEMPLATES       Name of specific template to export
  --out-dir OUT_DIR           Directory to output templates to.
  --debug                     Enable debug mode, this will show you all the json-rpc calls and responses
  --url URL                   URL to the zabbix server (example: https://monitor.example.com/zabbix )
  --user USER                 The zabbix api user
  --password PASSWORD         The zabbix api password
```



## License

Copyright (c) 2016, `Chegg Inc.`

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
