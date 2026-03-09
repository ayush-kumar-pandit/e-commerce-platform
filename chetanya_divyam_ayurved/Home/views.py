from django.shortcuts import render

# Create your views here.

def index(request):
    
    return render(request, 'index.html',context = {'Client': 'Rahul Bansal',
           'Developer': 'Ayush Pandit'} )