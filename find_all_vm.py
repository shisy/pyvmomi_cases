#!/usr/bin/env python
# -*- coding: utf-8 -*-

import atexit

from pyVim import connect
try:
    from pyVmomi import vmodl
except ImportError:
    pass

# import tools.cli as cli


def print_vm_info(virtual_machine, depth=1):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    maxdepth = 10

    # if this is a group it will have children. if it does, recurse into them
    # and then return
    if hasattr(virtual_machine, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = virtual_machine.childEntity
        for c in vmList:
            print_vm_info(c, depth + 1)
        return

    summary = virtual_machine.summary
    print("Name       : ", summary.config.name)
    print("Path       : ", summary.config.vmPathName)
    print("Guest      : ", summary.config.guestFullName)
    print("Instance UUID : ", summary.config.instanceUuid)
    print("Bios UUID     : ", summary.config.uuid)
    annotation = summary.config.annotation
    if annotation:
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
        if tools_version is not None:
            print("VMware-tools: ", tools_version)
        else:
            print("Vmware-tools: None")
        if ip_address:
            print("IP         : ", ip_address)
        else:
            print("IP         : None")
    if summary.runtime.question is not None:
        print("Question  : ", summary.runtime.question.text)
    print("")


def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """

    # args = cli.get_args()

    try:
        service_instance = connect.SmartConnect(host='172.16.6.197',
                                                user='root',
                                                pwd='dnt.com',
                                                port=443)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        children = content.rootFolder.childEntity
        for child in children:
            if hasattr(child, 'vmFolder'):
                datacenter = child
            else:
                # some other non-datacenter type object
                continue

            vm_folder = datacenter.vmFolder
            vm_list = vm_folder.childEntity
            for virtual_machine in vm_list:
                print_vm_info(virtual_machine, 10)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()