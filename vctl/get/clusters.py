import click
from pyVmomi import vim, vmodl

from vctl.helpers.vmware import get_obj
from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.exceptions.exceptions import ContextNotFound


#  @click.command()
#  def clusters():
#      try:
#          context = load_context()
#          si = inject_token(context)
#          content = si.content
#          hosts = get_obj(content, [vim.ComputeResource])
#          print('{:<30}{:<15}{:<15}{:<30}'.format(
#                'NAME', 'MEMORY %', 'CPU %', 'SPEC'))
#          for host in hosts:
#              print('{:<30}{:<15}{:<15}{:<30}'.format(host.name,
#                                                      '',
#                                                      '',
#                                                      host.parent.name))
#      except ContextNotFound:
#          print('Context not found.')
#      except vim.fault.NotAuthenticated:
#          print('Context expired.')
#      except Exception as e:
#          print('Caught error:', e)
