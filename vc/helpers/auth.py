import base64

from pyVmomi import vim, vmodl, SoapStubAdapter

from vc.helpers.vmware import get_unverified_context


def inject_token(context):
    soapStub = SoapStubAdapter(host=context['vcenter'], 
                               ns="vim25/5.5", 
                               sslContext=get_unverified_context(), 
                               connectionPoolTimeout=-1)
    si = vim.ServiceInstance("ServiceInstance", soapStub)
    si._stub.cookie = context['token']
    return si


def decode_token(token):
    b_token = base64.b64decode(token)
    cookie = b_token.decode('UTF-8')
    return cookie