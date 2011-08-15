"""
View functions for Sharrock.
"""
from sharrock import registry
from sharrock.descriptors import ParamRequired, MethodNotAllowed
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse

def check_extension(extension):
    if not extension in ['html','xml','json']:
        raise Http404

mtype_map = {'html':'text/html','xml':'application/xml','json':'application/json'}

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
    return render_to_response('sharrock/directory.%s' % extension,{'descriptors':descriptors})


def describe_service(request,app,version,service_name,extension='html'):
    """
    Gets a function descriptor.
    """
    check_extension(extension)

    try:
        return render_to_response('sharrock/descriptor.%s' % extension,
                                  {'descriptor':registry.get_descriptor(app,version,service_name)})
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
        return response
    except KeyError:
        raise Http404
    except ParamRequired as pr:
        return HttpResponse(str(pr),status=400) # missing parameter

def execute_resource(request,app,version,resource_name,extension='json'):
    """
    Executes the specified resource.
    """
    check_extension(extension)

    try:
        resource = registry.get_resource(app,version,resource_name)
        status_code, response_headers, serialized_result = resource.http_service(request,format=extension)
        response = HttpResponse(content=serialized_result,mimetype=response_headers['Content-type'],status=status_code)
        for header_name, header_value  in response_headers.items():
            response[header_name] = header_value
        return response
    except KeyError:
        raise Http404
    except ParamRequired as pr:
        return HttpResponse(str(pr),status=400) # there is a missing required parameter
    except MethodNotAllowed as mna:
        return HttpResponse(str(mna),status=405) # the employed http method is not supported

def resource_directory(request,app=None,version=None,extension='html'):
    """
    Gets a complete directory of resources.
    """
    check_extension(extension)

    resources = registry.resource_directory(app_label=app,specified_version=version)
    return render_to_response('sharrock/resource_directory.%s' % extension,{'resources':resources,'noname':True})


