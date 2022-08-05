from django.http import HttpResponse


def talents_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.user_type == 'Talent':
             return view_func(request, *args, **kwargs)
        else:
            return HttpResponse('You are not authorised to view this page')
    return wrapper_func

def hunters_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.user_type == 'Hunter':
             return view_func(request, *args, **kwargs)
        else:
            return HttpResponse('You are not authorised to view this page')
    return wrapper_func