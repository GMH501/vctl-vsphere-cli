import click
from pyVmomi import vim, vmodl

from vctl.helpers.vmware import get_obj
from vctl.helpers.helpers import load_context
from vctl.helpers.auth import inject_token
from vctl.exceptions.exceptions import ContextNotFound


@click.command()
@click.option('--context', '-c',
              help='the context you want to use for run this command, default is current-context.',
              required=False)
@click.option('--filter', '-f',
              help='Filters the output by network type.',
              type=click.Choice(['dvs']),
              required=False)
def networks(context, filter):
    try:
        context = load_context(context=context)
        si = inject_token(context)
        content = si.content
        networks = get_obj(content, [vim.Network])
        max_len = str(len(max([network.name for network in networks], key=len)) + 4)
        if filter is None:
            header_format = '{:<' + max_len + '}{:<15}{:<10}{:<8}'
            output_format = '{:<' + max_len + '}{:<15}{:<10}{:<8}'
            print(header_format.format(
                'NAME',
                'TYPE',
                'HOSTS',
                'VMS'
                )
            )
            for network in networks:
                if isinstance(network, vim.dvs.DistributedVirtualPortgroup):
                    _type = 'Distributed'
                else:
                    _type = 'Standard'
                print(output_format.format(
                    network.name,
                    _type,
                    len(network.host),
                    len(network.vm)
                    )
                )
        else:
            header_format = '{:<' + max_len + '}{:<15}{:<10}{:<8}{}'
            output_format = '{:<' + max_len + '}{:<15}{:<10}{:<8}{}'
            print(header_format.format(
                'NAME',
                'TYPE',
                'HOSTS',
                'VMS',
                'VLAN ID'
                )
            )
            for network in networks:
                if isinstance(network, vim.dvs.DistributedVirtualPortgroup):
                    _type = 'Distributed'
                else:
                    continue
                vlan = network.config.defaultPortConfig.vlan.vlanId 
                vlan_id = vlan if type(vlan) == int else '{}-{}'.format(vlan[0].start, vlan[0].end)
                print(output_format.format(
                    network.name,
                    _type,
                    len(network.host),
                    len(network.vm),
                    vlan_id
                    )
                )

    except vim.fault.NotAuthenticated:
        print('Context expired.')
        raise SystemExit(-1)
    except vmodl.MethodFault as e:
        print('Caught vmodl fault: {}'.format(e.msg))
        raise SystemExit(-1)
    except Exception as e:
        print('Caught error: {}'.format(e))
        raise SystemExit(-1)