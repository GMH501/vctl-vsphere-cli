import ssl

from pyVmomi import vim


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
            if name in c.name:
                obj = c
                break
        container.Destroy()
        return obj
    container.Destroy()
    return objects


def objectsInFolder(content, folder) -> list:
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.Folder],
                                                        True)
    for c in container.view:
        if folder == c.name:
            obj = c
            break
    container.Destroy()
    return obj.childEntity


def yeldVmsInFolder(objects):
    for obj in objects:
        if isinstance(obj, vim.VirtualMachine):
            yield obj
        if isinstance(obj, vim.Folder):
            yield from yeldVmsInFolder(obj.childEntity)


def yeldVmsInCluster(hosts):
    for host in hosts:
        for vm in host.vm:
            if isinstance(vm, vim.VirtualMachine):
                yield vm


def get_vm_hardware_lists(hardware):
    disk_list = []
    network_list = []
    for vm_hardware in hardware.device:
        if (vm_hardware.key >= 2000) and (vm_hardware.key < 3000):
            disk_list.append(
                {
                    'label': vm_hardware.deviceInfo.label,
                    'fileName': vm_hardware.backing.fileName,
                    'capacityInGB': vm_hardware.capacityInKB / 1024 / 1024,
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
            'vmPath': config.vmPathName,
            'uuid': config.uuid,
            'guestId': config.guestId,
            'template': config.template
        },
        'guest': {
            'hostname': guest.hostName,
            'guestOS': guest.guestFullName,
            'ipAddress': guest.ipAddress,
            'toolsStatus': str(guest.toolsStatus),
            'hwVersion': guest.hwVersion
        },
        'runtime': {
            'host': runtime.host.name,
            'bootTime': None,
            'connectionState': str(runtime.connectionState),
            'powerState': str(runtime.powerState)
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
        vm_obj['runtime']['bootTime'] = runtime.bootTime.strftime("%a, %d %b %Y %H:%M:%S %z")
    vm_obj['hardware']['virtualDisks'], \
        vm_obj['hardware']['virtualNics'] = get_vm_hardware_lists(hardware)
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
            'memorySize': int(hardware.memorySize),
            'cpuModel': hardware.cpuModel,
            'numCpuPkgs': int(hardware.numCpuPkgs),
            'numCpuCores': int(hardware.numCpuCores),
            'numCpuThreads': int(hardware.numCpuThreads),
            'numNics': int(hardware.numNics),
            'numHBAs': int(hardware.numHBAs)
        },
        'runtime': {
            'inMaintenanceMode': runtime.inMaintenanceMode,
            'bootTime': None,
            'connectionState': str(runtime.connectionState),
            'powerState': str(runtime.powerState),
            'standbyMode': str(runtime.standbyMode)
        }
    }
    if runtime.bootTime is not None:
        host_obj['runtime']['bootTime'] = runtime.bootTime.strftime("%a, %d %b %Y %H:%M:%S %z")
    return host_obj


def snapshot_tree(snap_list):
    output = []
    for snapshot in snap_list:
        snap_info = {}
        snap_info['snapshot'] = snapshot.snapshot._moId
        snap_info['id'] = snapshot.id
        snap_info['name'] = snapshot.name
        snap_info['description'] = snapshot.description
        snap_info['createTime'] = snapshot.createTime.strftime("%a, %d %b %Y %H:%M:%S %z")
        snap_info['state'] = str(snapshot.state)
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
    """Search recursively for the snapshot with the specified name.

    Args:
        snapshot_list (list): vm.snapshot.rootSnapshotList
        name (string) : snapshot name

    Return:
        vim.vm.Snapshot else None
    """
    output = None
    for snap in snapshot_list:
        if snap.name == name:
            output = snap.snapshot
            break
        if snap.childSnapshotList != []:
            output = search_snapshot(snap.childSnapshotList, name)
    return output


def procs_obj(procs):
    procs_list = []
    for proc in procs:
        obj = {
            'name': proc.name,
            'pid': proc.pid,
            'owner': proc.owner,
            'cmdLine': proc.cmdLine,
            'exitCode': str(proc.exitCode)
        }
        if proc.startTime is not None:
            obj['startTime'] = proc.startTime.strftime("%a, %d %b %Y %H:%M:%S %z")
        else:
            obj['startTime'] = str(None)
        if proc.endTime is not None:
            obj['endTime'] = proc.startTime.strftime("%a, %d %b %Y %H:%M:%S %z")
        else:
            obj['endTime'] = str(None)
        procs_list.append(obj)
    return procs_list