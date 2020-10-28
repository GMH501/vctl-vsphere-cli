[![Build Status](https://travis-ci.com/GMH501/vctl-vsphere-cli.svg?token=WbrqYj2c7b5z38d73y3B&branch=master)](https://travis-ci.com/GMH501/vctl-vsphere-cli) [![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/) [![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](https://opensource.org/licenses/Apache-2.0)
## VCTL
### An API based command line utility for inspecting and managing vCenter environments.

### Installation
```py
python -m pip install vctl
```
### Getting Started

To create a context:
```
C:\Users\gabriel>vctl context create -v vlab.example.local -u user -p password
```

### Usage examples
List the virtual machines on the host (esxi or vcenter):
```
C:\Users\gabriel>vctl get vms --format
NAME              HOSTNAME    MEMORY(MB)     CPU     IPADDRESS         STATUS         HOST
DC0_H0_VM0        None        32             1       None              poweredOn      DC0_H0
DC0_H0_VM1        None        32             1       None              poweredOn      DC0_H0
DC0_C0_RP0_VM0    None        32             1       None              poweredOn      DC0_C0_H2
DC0_C0_RP0_VM1    None        32             1       None              poweredOn      DC0_C0_H0
DC0_C1_RP0_VM0    None        32             1       None              poweredOn      DC0_C1_H2
DC0_C1_RP0_VM1    None        32             1       None              poweredOn      DC0_C1_H2
```

Get a virtual machine configuration in YAML format:
```
C:\Users\gabriel>vctl describe vm DC0_H0_VM0 -o yaml
config:
  name: DC0_H0_VM0
  vmPath: '[LocalDS_0] DC0_H0_VM0/DC0_H0_VM0.vmx'
  uuid: 265104de-1472-547c-b873-6dc7883fb6cb
  guestId: otherGuest
  template: false
guest:
  hostname: null
  guestOS: null
  ipAddress: null
  toolsStatus: toolsNotInstalled
  hwVersion: null
runtime:
  host: DC0_H0
  bootTime: Fri, 31 Jul 2020 09:52:45 +0200
  connectionState: connected
  powerState: poweredOn
hardware:
  numCPU: 1
  numCoresPerSocket: 1
  memoryMB: 32
  numEthernetCards: 1
  numVirtualDisks: 1
  virtualDisks: []
  virtualNics:
  - label: ethernet-0
    summary: 'DVSwitch: fea97929-4b2d-5972-b146-930c6d0b4014'
    macAddress: 00:0c:29:36:63:62
```

Execute a snapshot on a virtual machine:
```
C:\Users\gabriel>vctl vm DC0_H0_VM0 snapshot create -n snapshot_test -d description --quiesce --wait

C:\Users\gabriel>vctl vm DC0_H0_VM0 snapshot list -o yaml
snapshotInfo:
  currentSnapshot: snapshot-105
  rootSnapshotList:
  - snapshot: snapshot-105
    id: 1
    name: snapshot_test
    description: description
    createTime: Fri, 31 Jul 2020 10:07:21 +0200
    state: poweredOn
    quiesced: true
```
