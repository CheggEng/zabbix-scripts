# zabbix-scripts

## zabbixMaintenance.py
This is a tool for modifying hosts (or multiple host contained in a hostgroup).  It has the ability to disable, enable, place in maintenance mode, end a maintenance mode or even delete host(s).

Requires: 

* [https://github.com/blacked/py-zabbix](https://github.com/blacked/py-zabbix) ```pip install py-zabbix``` 


### Arguments

```
example-host user$ ./zabbixMaintenance.py -h
usage: zabbixMaintenance.py [-h] [--hostname HOSTNAME] [--hostgroup HOSTGROUP]
                            [--delete] [--enable] [--disable] [--maintenance]
                            [--maintenance-length] [--end-maintenance]
                            [--debug] --url URL --user USER --password
                            PASSWORD

This is a tool for modifying hosts (or multiple host contained in a
hostgroup). It has the ability to disable, enable, place in maintenance mode,
end a maintenance mode or even delete host(s).

optional arguments:
  -h, --help            show this help message and exit
  --hostname HOSTNAME   Hostname to modify
  --hostgroup HOSTGROUP Hostgroup to modify
  --delete              Flag that indicates we want to delete the host in question
  --enable              Flag that indicates we want to enable the host in question
  --disable             Flag that indicates we want to disable the host in question
  --maintenance         Flag that indicates we want to place the host in maintenance mode
  --maintenance-length  How long in seconds to be in maintenance mode. (default: 3600)
  --end-maintenance     Flag that indicates we want to disable maintenance mode
  --debug               nable debug mode, this will show you all the json-rpc calls and responses
  --url URL             URL to the zabbix server (example: https://monitor.example.com/zabbix)
  --user USER           The zabbix api user
  --password PASSWORD   The zabbix api password
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


## License

Copyright (c) 2016, `Chegg Inc.`
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
* Neither the name of the `<organization>` nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Chegg Inc. BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.