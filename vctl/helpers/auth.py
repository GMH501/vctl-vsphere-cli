import base64

from pyVmomi import vim, vmodl, SoapStubAdapter

from vctl.helpers.vmware import get_unverified_context


def inject_token(context):
    ns = '{}{}'.format('vim25/', context['apiversion'])
    soapStub = SoapStubAdapter(host=context['vcenter'], 
                               ns=ns,
                               sslContext=get_unverified_context(), 
                               connectionPoolTimeout=-1)
    si = vim.ServiceInstance("ServiceInstance", soapStub)
    si._stub.cookie = context['token']
    return si


def decode_token(token):
    b_token = base64.b64decode(token)
    cookie = b_token.decode('UTF-8')
    return cookie