from django.shortcuts import render

# Create your views here.

def index(request):
    # dic = {'Client': 'Rahul Bansal',
    #        'Developer': 'Ayush Pandit'}
    return render(request, 'index.html')