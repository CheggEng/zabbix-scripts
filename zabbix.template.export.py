#!/usr/bin/python

import argparse
import logging
import time
import os
import json
import xml.dom.minidom
from zabbix.api import ZabbixAPI
from sys import exit
from datetime import datetime

parser = argparse.ArgumentParser(description='This is a simple tool to export zabbix templates')
parser.add_argument('--templates', help='Name of specific template to export',default='All')
parser.add_argument('--out-dir', help='Directory to output templates to.',default='./templates')
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

  if None == args.url :
    print "Error: Missing --url\n\n"
    exit(2)

  if None == args.user :
    print "Error: Missing --user\n\n"
    exit(3)

  if None == args.password :
    print "Error: Missing --password\n\n"
    exit(4)

  if False == os.path.isdir(args.out_dir):
    os.mkdir(args.out_dir)

  zm = ZabbixTemplates( args.url, args.user, args.password )
  
  zm.exportTemplates(args)


class ZabbixTemplates:

    def __init__(self,_url,_user,_password):
      self.zapi = ZabbixAPI(url=_url, user=_user, password=_password)

    def exportTemplates(self,args):
      request_args = {
      	"output": "extend"
      }
      
      if args.templates != 'All':
        request_args.filter = {
          "host": [args.tempaltes]
        }
      
      result = self.zapi.do_request('template.get',request_args)
      if not result['result']:
        print "No matching host found for '{}'".format(hostname)
        exit(-3)
      
      if result['result']:
        for t in result['result']:
          dest = args.out_dir+'/'+t['host']+'.xml'
          self.exportTemplate(t['templateid'],dest)
          
    def exportTemplate(self,tid,oput):
      
      print "tempalteid:",tid," output:",oput
      args = {
        "options": {
            "templates": [tid]
        },
        "format": "xml"
      }
      
      result = self.zapi.do_request('configuration.export',args)
      template = xml.dom.minidom.parseString(result['result'].encode('utf-8'))
      date = template.getElementsByTagName("date")[0]
      # We are backing these up to git, steralize date so it doesn't appear to change 
      # each time we export the templates
      date.firstChild.replaceWholeText('2016-01-01T01:01:01Z')
      f = open(oput, 'w+')
      f.write(template.toprettyxml().encode('utf-8'))
      f.close()


if __name__ == '__main__':
  main()
