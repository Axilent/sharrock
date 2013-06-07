"""
View functions for Sharrock.
"""
from sharrock import registry
from sharrock.descriptors import ParamRequired, MethodNotAllowed, AccessDenied, Conflict
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from django.conf import settings
import logging

log = logging.getLogger('sharrock')

def check_extension(extension):
    if not extension in ['html','xml','json']:
        raise Http404

mtype_map = {'html':'text/html','xml':'application/xml','json':'application/json'}

api_root = '...'
if hasattr(settings,'SHARROCK_API_ROOT'):
    api_root = settings.SHARROCK_API_ROOT

resource_root = '...'
if hasattr(settings,'SHARROCK_RESOURCE_ROOT'):
    resource_root = settings.SHARROCK_RESOURCE_ROOT

def get_response_mimetype(extension):
    """
    Gets the proper MIME type for the http response.
    """
    return mtype_map[extension]

def directory(request,app=None,version=None,extension='html'):
    """
    Gets a complete directory of the function descriptors.
    """
    check_extension(extension)

    descriptors = registry.directory(app_label=app,specified_version=version)
    return render_to_response('sharrock/directory.%s' % extension,{'descriptors':descriptors,'api_root':api_root,'resource_root':resource_root})


def describe_service(request,app,version,service_name,extension='html',service_type='function'):
    """
    Gets a function descriptor.
    """
    check_extension(extension)

    try:
        if service_type == 'resource':
            return render_to_response('sharrock/resource.%s' % extension,
                                      {'resource':registry.get_descriptor(app,version,service_name),'api_root':api_root,'resource_root':resource_root})
        else:
            return render_to_response('sharrock/descriptor.%s' % extension,
                                      {'descriptor':registry.get_descriptor(app,version,service_name),'api_root':api_root,'resource_root':resource_root})
    except KeyError:
        raise Http404

def execute_service(request,app,version,service_name,extension='json'):
    """
    Executes the named service.
    """
    check_extension(extension)

    try:
        service = registry.get_descriptor(app,version,service_name)
        serialized_result = service.http_service(request,format=extension)
        response = HttpResponse(serialized_result,get_response_mimetype(extension))
        if service.is_deprecated:
            # set warning header
            response['Warning'] = 'METHOD DEPRECATED: %s' % service.is_deprecated
        return response
    except AccessDenied as ad:
        return HttpResponse(unicode(ad),status=403)
    except ParamRequired as pr:
        return HttpResponse(unicode(pr),status=400) # missing parameter
    except Conflict as con:
        return HttpResponse(unicode(con),status=409) # something user-resolvable is wrong with the function
    except BaseException as e:
        log.exception('Exception while accessing function %s.' % service_name)
        raise e

def execute_resource(request,app,version,resource_name,extension='json',model_id=None):
    """
    Executes the specified resource.
    """
    check_extension(extension)

    try:
        try:
            resource = registry.get_descriptor(app,version,resource_name)
        except KeyError:
            raise Http404
        status_code, response_headers, serialized_result = resource.http_service(request,format=extension)
        response = HttpResponse(content=serialized_result,mimetype=response_headers['Content-type'],status=status_code)
        for header_name, header_value  in response_headers.items():
            response[header_name] = header_value
        return response
    except AccessDenied as ad:
        return HttpResponse(unicode(ad),status=403) # access denied within the descriptor
    except ParamRequired as pr:
        return HttpResponse(unicode(pr),status=400) # there is a missing required parameter
    except MethodNotAllowed as mna:
        return HttpResponse(unicode(mna),status=405) # the employed http method is not supported
    except Conflict as con:
        return HttpResponse(unicode(con),status=409) # something user-resolvable is wrong with the resource
    except BaseException as e:
        log.exception('Exception while accessing resource %s.' % resource_name)
        raise e

def resource_directory(request,app=None,version=None,extension='html'):
    """
    Gets a complete directory of resources.
    """
    check_extension(extension)

    resources = registry.resource_directory(app_label=app,specified_version=version)
    return render_to_response('sharrock/resource_directory.%s' % extension,{'resources':resources,'noname':True})


