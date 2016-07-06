#!/usr/bin/python

import argparse
import logging
import time
from zabbix.api import ZabbixAPI
from sys import exit
from datetime import datetime
from os.path import basename

parser = argparse.ArgumentParser(description='This is a tool for modifying hosts (or multiple host contained in a hostgroup).  It has the ability to disable, enable, place in maintenance mode, end a maintenance mode or even delete host(s).')
parser.add_argument('--hostname', help='Hostname to modify')
parser.add_argument('--asset-tag', help='Find host by asset tag instead of hostname')
parser.add_argument('--hostgroup', help='Hostgroup to modify')
parser.add_argument('--delete', help='Flag that indicates we want to delete the host in question', action="store_true")
parser.add_argument('--create', help='Flag that indicates we want to create the host in zabbix', action="store_true")
parser.add_argument('--ip', help='Specify the ip for a host when creating a new host in zabbix')
parser.add_argument('--port', help='Specify the zabbix agent port for a host when creating a new host in zabbix. (default: 10050)', default='10050')
parser.add_argument('--proxy', help='If you are adding or updating a host and you want to specify a zabbix-proxy host to use.')
parser.add_argument('--templates', help='Add the following comma separated templates to a host, used when creating a new host',default='Linux')
parser.add_argument('--groups', help='Add the following comma separated groups to a host, used when creating a new host')
parser.add_argument('--enable', help='Flag that indicates we want to enable the host in question', action="store_true")
parser.add_argument('--disable', help='Flag that indicates we want to disable the host in question', action="store_true")
parser.add_argument('--maintenance', help='Flag that indicates we want to place the host in maintenance mode', action="store_true")
parser.add_argument('--maintenance-length', help='How long in seconds to be in maintenance mode. (default: 3600)',action="count", default=3600)
parser.add_argument('--end-maintenance', help='Flag that indicates we want to disable maintenance mode', action="store_true")
parser.add_argument('--debug', help='Enable debug mode, this will show you all the json-rpc calls and responses', action="store_true")
parser.add_argument('--url', help='URL to the zabbix server (example: https://monitor.example.com/zabbix)',required = True)
parser.add_argument('--user', help='The zabbix api user',required = True)
parser.add_argument('--password', help='The zabbix api password',required = True)
args = parser.parse_args()

if args.debug:
  logging.basicConfig(level = logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
  logger = logging.getLogger(__name__)

def main():
  global args
  global parser

  if None == args.hostname and None == args.hostgroup and None == args.asset_tag:
    print "Error: Missing --hostname, --asset-tag or --hostgroup\n\n"
    parser.print_help()
    exit(1)

  if None == args.url :
    print "Error: Missing --url\n\n"
    exit(2)

  if None == args.user :
    print "Error: Missing --user\n\n"
    exit(3)

  if None == args.password :
    print "Error: Missing --password\n\n"
    exit(4)


  zm = ZabbixMaintenance( args.url, args.user, args.password )


  if args.delete:
    if args.hostname or args.asset_tag:
      zm.deleteHost( args )
    elif args.hostgroup:
      zm.deleteHostgroup( args.hostgroup )
    else:
      print "Error deleting, no hostname or group specified"
  elif args.create:
    zm.createHost( args )
  elif args.enable:
    if args.hostname or args.asset_tag:
      zm.enableHost( args )
    elif args.hostgroup:
      zm.enableHostgroup( args.hostgroup )
    else:
      print "Error enabling, no hostname or group specified"
  elif args.disable:
    if args.hostname or args.asset_tag:
      zm.disableHost( args )
    elif args.hostgroup:
      zm.disableHostgroup( args.hostgroup )
    else:
      print "Error enabling, no hostname or group specified"
  elif args.maintenance:
    if args.hostname or args.asset_tag:
      zm.maintenanceMode( args,args.maintenance_length )
    elif args.hostgroup:
      zm.maintenanceModeHostgroup( args.hostgroup,args.maintenance_length )
    else:
      print "Error creating maintenance mode, no hostname or group specified"
  elif args.end_maintenance:
    if args.hostname or args.asset_tag:
      zm.endMaintenanceMode( args )
    elif args.hostgroup:
      zm.endMaintenanceModeHostgroup( args.hostgroup )
    else:
      print "Error creating maintenance mode, no hostname or group specified"
  else:
    print "Error: Must give either --enable, --disable, --delete, --maintenance or --end-maintenance flag\n\n"
    exit(-1)

class ZabbixMaintenance:

    def __init__(self,_url,_user,_password):
      self.zapi = ZabbixAPI(url=_url, user=_user, password=_password)

    def getHostByName(self,hostname):
      args = {
      	"output": [
          "hostid",
          "host"
        ],
        "filter": {
          "host": hostname
        }
      }
      result = self.zapi.do_request('host.get',args)
      if not result['result']:
        print "No matching host found for '{}'".format(hostname)
        exit(-3)
      return result['result'][0]

    def getHostByAssetTag(self,asset_tag):
      args = {
      	"output": [
          "hostid",
          "host"
        ],
        "searchInventory": {
            "asset_tag": asset_tag
        }
      }
      result = self.zapi.do_request('host.get',args)
      if not result['result']:
        print "No matching host found for '{}'".format(asset_tag)
        exit(-3)
      return result['result'][0]

    def getTemplateIDs(self, template_string):
      templates = map(str.strip, template_string.split(",") )
      template_ids = []

      request_args = {
        "output": "extend",
        "filter": {
            "host": templates
        }
      }
      result = self.zapi.do_request('template.get',request_args)
      if result['result']:
        for t in result['result']:
          template_ids.append({"templateid": t['templateid']})

      return template_ids

    def getGroupIDs(self, group_string):
      groups = map(str.strip, group_string.split(",") )
      group_ids = []

      request_args = {
        "output": "extend",
        "filter": {
            "name": groups
        }
      }
      result = self.zapi.do_request('hostgroup.get',request_args)
      if result['result']:
        for t in result['result']:
          group_ids.append({"groupid": t['groupid']})

      return group_ids

    def createHost(self, args):
      hostname = args.hostname
      cmd = 'host.create'
      if args.ip:
        ip = args.ip
      else:
        ip = ''

      # We should check if this host already exists and make it an update if it is
      search_request = {
      	"output": [
          "hostid",
          "host"
        ],
        "filter": {
          "host": hostname
        }
      }
      search_result = self.zapi.do_request('host.get',search_request)

      request_args = {
        "host": hostname,
        "interfaces": [
            {
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": hostname,
                "port": args.port
            }
        ],
        "inventory_mode": 1,
        "inventory": {
          "installer_name": "Created with zabbixMaintenance"
        }
      }

      if args.proxy:
        request_args['proxy_hostid'] = self.findProxyID(args.proxy)

      # If we found a matching host, lets include the hostid to make this an update
      if search_result['result']:
        if search_result['result'][0]:
          if search_result['result'][0]['hostid']:
            request_args['hostid'] = search_result['result'][0]['hostid']
            cmd = 'host.update'
            del request_args['interfaces']
            self.updataeInterface(search_result['result'][0]['hostid'],hostname,ip,args.port)

      if args.templates:
        request_args['templates'] = self.getTemplateIDs(args.templates)

      if args.groups:
        request_args['groups'] = self.getGroupIDs(args.groups)

      try:
        result = self.zapi.do_request(cmd,request_args)
        return result
      except:
        print "Error creating host or updating host."
        return []

    def findProxyID(self,proxy):
      cmd = 'proxy.get'
      request_args = {
        "output": "extend",
        "selectInterfaces": "extend",
        "filter": {
          "host": proxy
        }
      }

      try:
        result = self.zapi.do_request(cmd,request_args)
        return result['result'][0]['proxyid']
      except:
        print "Error creating host or updating host."
        return []


    def updataeInterface(self,hostid,hostname,ip,port):
      host_search_args = {
        "output": "extend",
        "hostids": hostid
      }

      try:
        host_search_result = self.zapi.do_request("hostinterface.get",host_search_args)

        #Find main int
        for zabbix_int in host_search_result['result']:
          if zabbix_int['main'] == "1":
            interface_update_args = {
              "interfaceid": zabbix_int['interfaceid'],
              "type": 1,
              "main": 1,
              "useip": 1,
              "ip": ip,
              "dns": hostname,
              "port": port
            }

            try:
              iterface_result = self.zapi.do_request("hostinterface.update",interface_update_args)
              return True
            except:
              print "Error updating host interface."
      except:
        print "Error finding host interface."

      return False

    def deleteHost(self,args):
      if args.asset_tag:
        _host = self.getHostByAssetTag(args.asset_tag)
      else:
        _host = self.getHostByName(args.hostname)

      request_args = [_host['hostid']]

      result = self.zapi.do_request('host.delete',request_args)
      return result

    def enableHost(self,args):
      if args.asset_tag:
        _host = self.getHostByAssetTag(args.asset_tag)
      else:
        _host = self.getHostByName(args.hostname)

      request_args = {
        "hostid": _host['hostid'],
        "status": 0
      }
      result = self.zapi.do_request('host.update',request_args)
      return result

    def disableHost(self,args):
      if args.asset_tag:
        _host = self.getHostByAssetTag(args.asset_tag)
      else:
        _host = self.getHostByName(args.hostname)

      request_args = {
        "hostid": _host['hostid'],
        "status": 1
      }
      result = self.zapi.do_request('host.update',request_args)
      return result

    def maintenanceMode(self,args,timeWindow):
      if args.asset_tag:
        _host = self.getHostByAssetTag(args.asset_tag)
      else:
        _host = self.getHostByName(args.hostname)

      d = datetime.now()
      currentDate = d.strftime("%c")
      request_args = {
        "name": "Generated by {0} on {1} for {2}".format(basename(__file__),currentDate,hostname),
        "active_since": int(time.time()),
        "active_till": int(time.time()+timeWindow),
        "hostids": [
          _host['hostid']
        ],
        "timeperiods": [
          {
            "timeperiod_type": 0,
            "period": timeWindow
          }
        ]
      }
      result = self.zapi.do_request('maintenance.create',request_args)
      return


    def getMaintenance(self,hostid):

      args = {
        "output": "extend",
        "selectTimeperiods": "extend",
        "hostids": hostid
      }
      result = self.zapi.do_request('maintenance.get',args)
      return result['result']

    def endMaintenanceMode(self,args):
      if args.asset_tag:
        _host = self.getHostByAssetTag(args.asset_tag)
      else:
        _host = self.getHostByName(args.hostname)

      _maintenance = self.getMaintenance(_host['hostid'])
      _maintenance_ids = []
      n = int(time.time())

      for maintenance_id in _maintenance:
        if int(maintenance_id['active_since']) < int(n) and int(maintenance_id['active_till']) > int(n):
          _maintenance_ids.append(maintenance_id['maintenanceid'])
          maintenance_id['active_till'] = n
          maintenance_id['hostids'] = [ _host['hostid'] ]
          result = self.zapi.do_request('maintenance.update',maintenance_id)

      if not _maintenance_ids:
        if args.asset_tag:
          print "No valid maintenance windows defined for the asset-tag {0}".format(args.asset_tag)
        else:
          print "No valid maintenance windows defined for the host {0}".format(args.hostname)
        exit(-4)

      return _maintenance_ids


    def getHostGroupByName(self,hostgroup):
      args = {
      	"selectHosts": "extend",
        "filter": {
          "name": hostgroup
        }
      }
      result = self.zapi.do_request('hostgroup.get',args)
      if not result['result']:
        print "No matching hostgroup found for '{}'".format(hostgroup)
        exit(-5)
      return result['result'][0]


    def deleteHostgroup(self,hostgroup):
      _hostgroup = self.getHostGroupByName(hostgroup)
      hosts = []
      for h in _hostgroup['hosts']:
        hosts.append(h['hostid'])

      args = hosts

      result = self.zapi.do_request('host.delete',args)
      return result

    def enableHostgroup(self,hostgroup):
      _hostgroup = self.getHostGroupByName(hostgroup)
      hosts = []
      for h in _hostgroup['hosts']:
        hosts.append({"hostid": h['hostid']})

      args = {
        "hosts": hosts,
        "status": 0
      }
      result = self.zapi.do_request('host.massupdate',args)
      return result

    def disableHostgroup(self,hostgroup):
      _hostgroup = self.getHostGroupByName(hostgroup)
      hosts = []
      for h in _hostgroup['hosts']:
        hosts.append({"hostid": h['hostid']})

      args = {
        "hosts": hosts,
        "status": 1
      }
      result = self.zapi.do_request('host.massupdate',args)
      return result

    def maintenanceModeHostgroup(self,hostgroup,timeWindow):
      _hostgroup = self.getHostGroupByName(hostgroup)


      d = datetime.now()
      currentDate = d.strftime("%c")
      args = {
        "name": "Generated by {0} on {1} for hostgroup {2}".format(basename(__file__),currentDate,hostgroup),
        "active_since": int(time.time()),
        "active_till": int(time.time()+timeWindow),
        "groupids": [_hostgroup['groupid']],
        "timeperiods": [
          {
            "timeperiod_type": 0,
            "period": timeWindow
          }
        ]
      }
      result = self.zapi.do_request('maintenance.create',args)
      return result

    def getMaintenanceByHostGroup(self,groupid):

      args = {
        "output": "extend",
        "selectTimeperiods": "extend",
        "groupids": groupid
      }
      result = self.zapi.do_request('maintenance.get',args)
      return result['result']

    def endMaintenanceModeHostgroup(self,hostgroup):
      _hostgroup = self.getHostGroupByName(hostgroup)
      _maintenance = self.getMaintenanceByHostGroup(_hostgroup['groupid'])
      _maintenance_ids = []
      n = int(time.time())

      for maintenance_id in _maintenance:
        if int(maintenance_id['active_since']) < int(n) and int(maintenance_id['active_till']) > int(n):
          _maintenance_ids.append(maintenance_id['maintenanceid'])
          maintenance_id['active_till'] = n
          maintenance_id['groupids'] = [ _hostgroup['groupid'] ]

          print "maintenance.update args"
          print maintenance_id
          result = self.zapi.do_request('maintenance.update',maintenance_id)

      if not _maintenance_ids:
        print "No valid maintenance windows defined for the hostgroup {0}".format(hostgroup)
        exit(-4)

      return _maintenance_ids

if __name__ == '__main__':
  main()
