#!/usr/bin/python

import argparse
import logging
import time
import os
import re
from boto.s3.connection import S3Connection
from urlparse import urlparse
from sys import exit
from datetime import datetime


parser = argparse.ArgumentParser(description='This is a tool for modifying hosts (or multiple host contained in a hostgroup).  It has the ability to disable, enable, place in maintenance mode, end a maintenance mode or even delete host(s).')
parser.add_argument('--url', help='path to s3 file (ex: s3://zabbix-ops/monitors/check_table_partition.txt)',required = True)
parser.add_argument('--regex', help='Simple reges to apply to file contents')
parser.add_argument('--ttl', help='File age in seconds')
parser.add_argument('--access_key', help='AWS Access key ID')
parser.add_argument('--secret_key', help='AWS Secret Password')
parser.add_argument('--aws_profile', help='AWS profile to use from ~/.aws/credentials file')
parser.add_argument('--debug', help='Enable debug mode, this will show you all the json-rpc calls and responses', action="store_true")

args = parser.parse_args()

if args.debug:
  logging.basicConfig(level = logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
  logger = logging.getLogger(__name__)

def main():
  global args
  tmpfile = '/tmp/.s3.tmp'

  o = urlparse(args.url)
  if args.debug:
    print o

  if args.access_key and args.secret_key:
    conn = S3Connection(args.access_key, args.secret_key)
  elif args.aws_profile:
    conn = S3Connection(profile_name=args.aws_profile)
  else:
    conn = S3Connection()

  bucket = conn.get_bucket(o.netloc)
  s3_file = bucket.get_key(o.path)
  s3_file.get_contents_to_filename(tmpfile)
  if args.debug:
    print s3_file


  if args.ttl:
    stats = os.stat(tmpfile)
    n = int(time.time())
    delta = int(n - stats.st_mtime)
    if args.debug:
      print "Delta =",delta,", ttl =",args.ttl
    if int(args.ttl) < int(delta):
      print 'Error: file too old'
      exit(-1)


  if args.regex:
    mys3temp = open(tmpfile,"r")
    fc = mys3temp.read()
    m = re.search(args.regex,fc)
    if args.debug:
      print fc
    if m:
      pass
    else:
      print "Error: regex failed to match '%s'" % args.regex
      exit(-2)

  os.remove(tmpfile)
  print "FOUND-OK"

if __name__ == '__main__':
  main()