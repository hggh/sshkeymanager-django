#!/usr/bin/env python
# 2015 - Jonas Genannt <jonas@brachium-system.net>
# License: GPLv2
#
# This script works on Python2 and Python3
#
# this script is used with the SSHKey Manager Django app
# you can deploy ssh public keys to your hosts

import argparse
import os
import requests
import tempfile
import shutil
from datetime import datetime
try:
  import ConfigParser
except:
  import configparser as ConfigParser
  pass



DEFAULT_CONFIG='/etc/skm-deploy.conf'
CONFIG=None
POST_DATA={}

def write_keys(directory, accounts):
  for acc in accounts:
    name = acc
    filename = os.path.join(directory, name)
    content = "### Deploy via skm-deploy on " + str(datetime.today()) + "\n" + "\n".join(accounts[name])
    with open(filename, 'w') as f:
      f.write(content)

def _get_config(filename):
  setting = ConfigParser.ConfigParser()
  setting.read(filename)
  cfg = {}
  for opt in setting.options('default'):
    cfg[opt] = setting.get('default', opt)
  return cfg

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-t', '--filter-type', help='run filter against: [group|environment|host]')
  parser.add_argument('-f', '--filter-value', help='filter value.')
  parser.add_argument('-c', '--config', help='configration with secret token and URL to webservice. defaults: /etc/skm-deploy.conf')
  args = parser.parse_args()

  if args.config:
    CONFIG=args.config
  else:
    CONFIG=DEFAULT_CONFIG

  if os.access(CONFIG, os.R_OK) is False:
    print('Error: Could not open configuration for reading: ' + CONFIG)
    exit(1)

  if args.filter_type:
    if args.filter_type not in [ 'group', 'host', 'environemnt' ]:
      print("Error: Unkown filter type argument: " + args.filter_type)
      exit(1)
    if args.filter_value is None:
      print("Error: if setting --filter-type, please add a filter-value")
      exit(1)
    POST_DATA['filter_type'] = args.filter_type
    POST_DATA['filter_value'] = args.filter_value


  config = _get_config(CONFIG)
  POST_DATA['API_KEY'] = config['apikey']

  r = requests.post(config['address'], POST_DATA)

  if r.status_code != 200:
    print("Error: API Returned Status Code: " + str(r.status_code))
    exit(1)

  if len(r.json()) == 0:
    print("Warning: API returned a empty json. Please check filter and or accounts")
    exit(1);

  json = r.json()
  for key in json:
    host = json[key]
    connect = key
    if host['ip']:
      connect = host['ip']
    try:
      print("Info: Deploying Host: " + key)
      directory = tempfile.mkdtemp('_' + key, prefix='skm-deploy')
      write_keys(directory, host['accounts'])
      shutil.rmtree(directory)
    except Exception as e:
      print("Error: error on host " + key)
      pass
