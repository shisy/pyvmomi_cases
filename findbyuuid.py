import atexit
import argparse
import getpass

from pyVim import connect


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='Remote host to connect to')

    parser.add_argument('-o', '--port',
                        required=False,
                        action='store',
                        help="port to use, default 443", default=443)

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-d', '--uuid',
                        required=True,
                        action='store',
                        help='Instance UUID of the VM to look for.')

    args = parser.parse_args()
    if args.password is None:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))

    args = parser.parse_args()

    return args

args = get_args()

# form a connection...
si = connect.SmartConnect(host=args.host, user=args.user, pwd=args.password,
                          port=args.port)

# doing this means you don't need to remember to disconnect your script/objects
atexit.register(connect.Disconnect, si)

# see:
# http://pubs.vmware.com/vsphere-55/topic/com.vmware.wssdk.apiref.doc/vim.ServiceInstanceContent.html
# http://pubs.vmware.com/vsphere-55/topic/com.vmware.wssdk.apiref.doc/vim.SearchIndex.html
search_index = si.content.searchIndex
vm = search_index.FindByUuid(None, args.uuid, True, True)

if vm is None:
    print("Could not find virtual machine '{0}'".format(args.uuid))
    exit(1)

print("Found Virtual Machine")
details = {'name': vm.summary.config.name,
           'instance UUID': vm.summary.config.instanceUuid,
           'bios UUID': vm.summary.config.uuid,
           'path to VM': vm.summary.config.vmPathName,
           'guest OS id': vm.summary.config.guestId,
           'guest OS name': vm.summary.config.guestFullName,
           'host name': vm.runtime.host.name,
           'last booted timestamp': vm.runtime.bootTime,
           }

for name, value in details.items():
    print("{0:{width}{base}}: {1}".format(name, value, width=25, base='s'))