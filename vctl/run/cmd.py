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


def load_yaml(path):
    try:
        with open(path, 'r') as config_file:
            return list(yaml.safe_load_all(config_file))
    except FileNotFoundError:
        print('Runner not found in path: {}'.format(path))
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
            error ='Incorrect parameter: {} for function snapshot'.format(mode)
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


def with_vars(function, variables):
    FIND_VAR = re.compile('\$var.([\\w]*)')
    ### LA FUNZIONE SUPPORTA UN SOLO REPLACE PER STRINGA
    new_parameters = dict()
    for argument, parameter in function.items():
        if type(parameter) == str and parameter.count('$var.') == 1:
            try:
                key = re.findall(FIND_VAR, parameter)[0]
                variable = variables[key]
                REGEX_VAR = eval("re.compile(r'\$var\.{}')".format(key))
                if type(variable) == str:
                    new_param = re.sub(REGEX_VAR, variable, parameter)
                    new_parameters[argument] = new_param
                elif type(variable) == int:
                    new_param = re.sub(REGEX_VAR, str(variable), parameter)
                    new_parameters[argument] = int(new_param) \
                        if new_param.isdecimal() else new_param
                elif type(variable) == bool:
                    new_parameters[argument] = variable
            except KeyError:  ## se all'interno di un parameter trova una $var.<qualcosa> non conosciuta
                new_parameters[argument] = parameter
        elif type(parameter) == str and parameter.count('$var.') > 1:
            keys = re.findall(FIND_VAR, parameter)
            new_param = parameter
            for key in keys:
                if key in variables:
                    variable = variables[key]
                    REGEX_VAR = eval("re.compile(r'\$var\.{}')".format(key))
                    new_param = re.sub(REGEX_VAR, str(variable), new_param)
                else:
                    pass
            new_parameters[argument] = new_param
        else:
            new_parameters[argument] = parameter
    return new_parameters


def loop(function, item):
    LOOP_REGEX = re.compile('\$item')
    parameters = dict()
    for argument, parameter in function.items():
        if type(parameter) == str:
            subs_param = re.sub(LOOP_REGEX, str(item), parameter)
            parameters[argument] = subs_param
        else:
            parameters[argument] = parameter
    return parameters


def func_output(rc, log):
    if rc == 0:
        print('{}  rc => {}, log => {}{}'.format(Fore.YELLOW, rc, log, Fore.RESET))
    elif rc == 1:
        print('{}  rc => {}, log => {}{}'.format(Fore.RED, rc, log, Fore.RESET))
    elif rc == 2:
        pass

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
        documents = load_yaml(file_path)
        for document in documents:
            functions = list(document)
            if 'name' in functions:
                print('===> [{}]'.format(document['name']))
                functions.remove('name')
            for function in functions:
                if not eval('callable({})'.format(function)):
                    raise ValueError('function {} not defined.'.format(function))
            for function in functions:
                if function in ['loop', 'with_vars']:
                    continue
                func_params = document[function]
                if 'with_vars' in functions:
                    for variables in document['with_vars']:
                        new_params = with_vars(func_params, variables)
                        rc, log = eval(function + "(content=content, **new_params)")
                        func_output(rc, log)   
                elif 'loop' in functions:
                    for item in document['loop']:
                        new_params = loop(func_params, item)
                        rc, log = eval(function + "(content=content, **new_params)")
                        func_output(rc, log)
                else:
                    rc, log = eval(function + "(content=content, **func_params)")
                    func_output(rc, log)

    except Exception as e:
        print('{}Caught error: {}'.format(Fore.RESET, e))
        SystemExit(1)
