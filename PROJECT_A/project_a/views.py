# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

def login_page(request):
    return render(request, 'project_a/login.html')
