import ssl


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
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    objects = [i for i in container.view]
    if name:
     for c in container.view:
        if c.name == name:
            obj = c
            break
     container.Destroy()
     return obj
    else:
     container.Destroy()
     return objects