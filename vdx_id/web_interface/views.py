from django.shortcuts import render


######################
# Auth test decorator
######################
def index(request):
    request.session['new_visit'] = None
    return render(request, 'home.html', {})
