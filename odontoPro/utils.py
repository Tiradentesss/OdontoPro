from django.shortcuts import redirect

def clinica_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("clinica_id"):
            return redirect("login_clinica")
        return view_func(request, *args, **kwargs)
    return wrapper
