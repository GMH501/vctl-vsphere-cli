## #  https://stackoverflow.com/questions/990422/how-to-get-a-reference-to-current-modules-attributes-in-python

import inspect
import re
import time
import sys
import os
import yaml

import click
from colorama import init, Fore
from pyVmomi import vim, vmodl

from vctl.exceptions.exceptions import ContextNotFound
from vctl.helpers.auth import inject_token
from vctl.helpers.vmware import get_obj, snapshot_tree, snapshot_obj, search_snapshot
from vctl.helpers.helpers import load_context, jsonify
from vctl.helpers.utils import waiting

try:
    from pyVim.task import WaitForTask
except:
    from pyvim.task import WaitForTask


init(convert=True)
REGEX = re.compile('\$item')


def loop():
    pass


def load_yaml(path):
    try:
        with open(path, 'r') as config_file:
            return list(yaml.safe_load_all(config_file))
    except FileNotFoundError:
        print('Config file not found.')
        raise SystemExit(1)


def get_path(file):
    file_path = file
    if not file.startswith('/') or file.startswith(':', 1):
            working_path = os.getcwd()
            file_path = os.path.join(working_path, file)
    return file_path


def power(content, vm, state, wait=True):
    try:
        _vm = get_obj(content, [vim.VirtualMachine], vm)
        if not isinstance(_vm, vim.VirtualMachine):
            raise NotImplementedError('virtual machine not found.')
        valid_state = ['on', True, 'off', False]
        if state not in valid_state:
            raise ValueError('state must be one of {}.'.format(['on', 'off']))
        if state:
            task = _vm.PowerOnVM_Task()
            state = 'On'
        else:
            task = _vm.PowerOffVM_Task()
            state = 'Off'
        if wait:
            WaitForTask(task)
            return 0, '{} vm powered{}.'.format(vm, state)
        else:
            return 2, None

    except vim.fault.NotAuthenticated:
        error = 'Caught vctl fault: Context expired.'
        return 1, error
    except vmodl.MethodFault as e:
        error = '{} Caught vmodl fault: {}'.format(vm, e.msg)
        return 1, error
    except Exception as e:
        error = '{} Caught error: {}'.format(vm, e)
        return 1, error


def snapshot(content, mode, vm, description, memory=False, quiesce=False, wait=True):
    """
    """
    try:
        _vm = get_obj(content, [vim.VirtualMachine], vm)
        if not isinstance(_vm, vim.VirtualMachine):
            raise NotImplementedError('virtual machine not found.')
        if mode == 'create':
            task = _vm.CreateSnapshot(vm, description, memory=memory, quiesce=quiesce)
            if wait:
                WaitForTask(task)
                return 0, '{} snapshot created.'.format(vm)
            else:
                return 2, None

        else:
            error ='Incorrect parameter: {}'.format(mode)
            raise SystemExit(error)

    except vim.fault.NotAuthenticated:
        error = 'Caught vctl fault: Context expired.'
        return 1, error
    except vmodl.MethodFault as e:
        error = '{} Caught vmodl fault: {}'.format(vm, e.msg)
        return 1, error
    except Exception as e:
        error = '{} Caught error: {}'.format(vm, e)
        return 1, error


@click.command()
@click.option('--context', '-c',
              help='The context to use for run the command, the default is <current-context>.',
              required=False)
@click.argument('file', nargs=1,
              required=True)
def run(file, context):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        file_path = get_path(file)
        tasks = load_yaml(file_path)
        for task in tasks:
            task_keys = list(task)
            if 'name' in task_keys:
                print('{}===> [{}]'.format(Fore.RESET, task['name']))
                task_keys.remove('name')
            for key in task_keys:
                if (key not in dir(sys.modules[__name__])) and \
                    key not in ['loop']:
                    raise ValueError('{}function {} not defined.'.format(Fore.RESET, key))
            for key in task_keys:
                if key in ['loop']:
                    continue
                function = key
                if 'loop' in task_keys:
                    for item in task['loop']:
                        parameters = dict()
                        for argument, parameter in task[function].items():
                            if type(parameter) == str:
                                subs_param = re.sub(REGEX, item, parameter)
                                parameters[argument] = subs_param
                            else:
                                parameters[argument] = parameter
                        rc, log = eval(function + "(content=content, **parameters)")
                        if rc == 0:
                            print('{}  rc => {}, log => {}'.format(Fore.YELLOW, rc, log))
                        elif rc == 1:
                            print('{}  rc => {}, log => {}'.format(Fore.RED, rc, log))
                        elif rc == 2:
                            pass
                else:
                    rc, log = eval(function + "(content=content, **task[function])")
                    if rc == 0:   # wait success
                        print('{}  rc => {}, log => {}'.format(Fore.GREEN, rc, log))
                    elif rc == 1: # wait error
                        print('{}  rc => {}, log => {}'.format(Fore.RED, rc, log))
                    elif rc == 2: # no wait
                        print('{}  rc => {}, log => {}'.format(Fore.RED, rc, log))

    except Exception as e:
        print('{}Caught error: {}'.format(Fore.RESET, e))
        SystemExit(1)
