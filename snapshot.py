#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import atexit

import requests

from pyVim.connect import SmartConnect, Disconnect

from tools import cli

requests.packages.urllib3.disable_warnings()


def setup_args():
    parser = cli.build_arg_parser()
    parser.add_argument('-j', '--uuid', required=True,
                        help="UUID of the VirtualMachine you want to find."
                             " If -i is not used BIOS UUID assumed.")
    parser.add_argument('-i', '--instance', required=False,
                        action='store_true',
                        help="Flag to indicate the UUID is an instance UUID")
    parser.add_argument('-d', '--description', required=False,
                        help="Description for the snapshot")
    parser.add_argument('-n', '--name', required=True,
                        help="Name for the Snapshot")
    my_args = parser.parse_args()
    return cli.prompt_for_password(my_args)


args = setup_args()
si = None
instance_search = False
try:
    si = SmartConnect(host=args.host,
                      user=args.user,
                      pwd=args.password,
                      port=int(args.port))
    atexit.register(Disconnect, si)
except IOError:
    pass

if not si:
    raise SystemExit("Unable to connect to host with supplied info.")
if args.instance:
    instance_search = True
vm = si.content.searchIndex.FindByUuid(None, args.uuid, True, instance_search)

if vm is None:
    raise SystemExit("Unable to locate VirtualMachine.")

desc = None
if args.description:
    desc = args.description

task = vm.CreateSnapshot_Task(name=args.name,
                              description=desc,
                              memory=True,
                              quiesce=False)


print("Snapshot Completed.")
del vm
vm = si.content.searchIndex.FindByUuid(None, args.uuid, True, instance_search)
snap_info = vm.snapshot

tree = snap_info.rootSnapshotList
while tree[0].childSnapshotList is not None:
    print("Snap: {0} => {1}".format(tree[0].name, tree[0].description))
    if len(tree[0].childSnapshotList) < 1:
        break
    tree = tree[0].childSnapshotList
