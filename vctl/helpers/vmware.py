import ssl
import datetime


def get_unverified_context():
    """
    Get an unverified ssl context. Used to disable the server certificate
    verification.
    @return: unverified ssl context.
    """
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    return context


def get_obj(content, vimtype, name=None):
    """
     Get the vsphere object associated with a given text name or vimtype.
    """
    obj = None
    objects = []
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype,
                                                        True)
    objects = [i for i in container.view]
    if name:
        for c in container.view:
            if c.name == name:
                obj = c
                break
        container.Destroy()
        return obj
    container.Destroy()
    return objects


def get_vm_hardware_lists(hardware):
    disk_list = []
    network_list = []
    for vm_hardware in hardware.device:
        if (vm_hardware.key >= 2000) and (vm_hardware.key < 3000):
            disk_list.append(
                {
                    'label': vm_hardware.deviceInfo.label,
                    'fileName': vm_hardware.backing.fileName,
                    'capacityInGB': vm_hardware.capacityInKB/1024/1024,
                    'thinProvisioned': vm_hardware.backing.thinProvisioned,
                }
            )
        elif (vm_hardware.key >= 4000) and (vm_hardware.key < 5000):
            network_list.append(
                {
                    'label': vm_hardware.deviceInfo.label,
                    'summary': vm_hardware.deviceInfo.summary,
                    'macAddress': vm_hardware.macAddress
                }
            )
    return disk_list, network_list


def get_vm_obj(vm):
    """this is a docstring try
    
    | :param vm: vim.VirtualMachine
    | :return:   dict containing vm spec
    | :rtype:    dict
    """
    summary = vm.summary
    config = summary.config
    guest = summary.guest
    runtime = summary.runtime
    hardware = vm.config.hardware
    vm_obj = {
        'config': {
            'name': config.name, 
            'vmPath': config.vmPathName
        },
        'guest': {
            'hostname':  guest.hostName,
            'guestOS': guest.guestFullName,
            'ipAddress': guest.ipAddress,
            'hwVersion': guest.hwVersion
        },
        'runtime': {
            'host': runtime.host.name,
            'bootTime': None,
            'connectionState': runtime.connectionState,
            'powerState': runtime.powerState
        },
        'hardware': {
            'numCPU': hardware.numCPU,
            'numCoresPerSocket': hardware.numCoresPerSocket,
            'memoryMB': hardware.memoryMB,
            'numEthernetCards': config.numEthernetCards,
            'numVirtualDisks': config.numVirtualDisks,
            'virtualDisks': [],
            'virtualNics': []
        }
    }
    if runtime.bootTime is not None:
        vm_obj['runtime']['bootTime'] = runtime.bootTime.strftime(
                                            "%a, %d %b %Y %H:%M:%S %z")
    disk_list, network_list = get_vm_hardware_lists(hardware)
    vm_obj['hardware']['virtualDisks'] = disk_list
    vm_obj['hardware']['virtualNics'] = network_list
    return vm_obj