from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.


class ListView(TemplateView):
    # Example of a function-based view
    template_name = "client/clientlist.html"