import ssl
import datetime


def get_unverified_context():
    """Get an unverified ssl context. 
    Used to disable the server certificate verification.

    @return: unverified ssl context.
    """
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    return context


def get_obj(content, vimtype, name=None):
    """Get the vsphere object associated with a given text name or vimtype.
    """
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype,
                                                        True)
    objects = list(container.view)
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
    """
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
                                            "%a, %d %b %Y %H:%M:%S %z"
                                            )
    disk_list, network_list = get_vm_hardware_lists(hardware)
    vm_obj['hardware']['virtualDisks'] = disk_list
    vm_obj['hardware']['virtualNics'] = network_list
    return vm_obj


def get_host_obj(host):
    summary = host.summary
    config = summary.config
    hardware = summary.hardware
    runtime = summary.runtime
    host_obj = {
        'config': {
            'name': config.name,
        },
        'hardware': {
            'vendor': hardware.vendor,
            'model': hardware.model,
            'memorySize': hardware.memorySize,
            'cpuModel': hardware.cpuModel,
            'numCpuPkgs': hardware.numCpuPkgs,
            'numCpuCores': hardware.numCpuCores,
            'numCpuThreads': hardware.numCpuThreads,
            'numNics': hardware.numNics,
            'numHBAs': hardware.numHBAs
        },
        'runtime': {
            'inMaintenanceMode': runtime.inMaintenanceMode,
            'bootTime': None,
            'connectionState': runtime.connectionState,
            'powerState': runtime.powerState,
            'standbyMode': runtime.standbyMode
        }
    }
    if runtime.bootTime is not None:
        host_obj['runtime']['bootTime'] = runtime.bootTime.strftime(
                                            "%a, %d %b %Y %H:%M:%S %z"
                                            )
    return host_obj


def snapshot_tree(snap_list):
    output = []
    for snapshot in snap_list:
        snap_info = {}
        snap_info['snapshot'] = snapshot.snapshot._moId
        snap_info['id'] = snapshot.id
        snap_info['name'] = snapshot.name
        snap_info['createTime'] = snapshot.createTime.strftime(
                                            "%a, %d %b %Y %H:%M:%S %z"
                                            )
        snap_info['state'] = snapshot.state
        snap_info['quiesced'] = snapshot.quiesced
        output.append(snap_info)
        if snapshot.childSnapshotList != []:
            snap_info['childSnapshotList'] = snapshot_tree(snapshot.childSnapshotList)
    return output


def snapshot_obj(snap):
    output = {
        'snapshotInfo': {
            'currentSnapshot': snap.currentSnapshot._moId,
            'rootSnapshotList': snapshot_tree(snap.rootSnapshotList)
        }
    }
    return output

def search_snapshot(snapshot_list, name):
    """
    :param root_snapshot : vm.snapshot.rootSnapshotList
    :type snapshot : list
    :return : vim.vm.Snapshot
    """
    output = None
    for snap in snapshot_list:
        if snap.name == name:
            output = snap.snapshot
            break
        if snap.childSnapshotList != []:
            output = search_snapshot(snap.childSnapshotList, name)
    return output
            