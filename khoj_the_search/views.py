from django.shortcuts import render
from rest_framework.views import APIView
from .models import KhojTheSearch
from .serializers import KhojAndSearchSerializer
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponse
import json
from django.core import serializers
from datetime import datetime

# Create your views here.
class KhojAndSearch(LoginRequiredMixin, View):
    login_url = 'http://127.0.0.1:8000/api/user/account/login/'
    redirect_field_name = ''
    def get(self, request):
        return render(request, 'khoj-the-search.html')
    
    serializer_class = KhojAndSearchSerializer
    def post(self, request, format=None):
        result = False
        inputValues = request.POST['input-values']
        searchValue = request.POST['search-value']
        
        
        if inputValues and searchValue:
            KhojTheSearch.objects.create(
                user = request.user,
                int_list = inputValues,
            )
            
            khoj = KhojTheSearch.objects.filter(user = request.user).values_list('int_list')
            for i in khoj:
                tts = i[0]
                values = [int(item) for item in tts.split(', ') if item.isdigit()]
                for item in values:
                    if int(searchValue) == item:
                        result =  True
                
            return JsonResponse(
                {
                    'message': result,
                })
        return JsonResponse({'message: Please enter value both fields'})


class AllInputValues(LoginRequiredMixin, View):
    login_url = 'http://127.0.0.1:8000/api/user/account/login/'
    redirect_field_name = ''
    # serializer_class = KhojAndSearchSerializer
    def get(self, request, format=None):
        message = 'failed'
        data = []
        dict = {}
        if request.user:
            message= 'success'
        
        khoj = KhojTheSearch.objects.filter(user = request.user)
        if khoj:
            message = 'success'
        for item in khoj:

            dict = {
                "timestamp": str(item.created_at),
                "input_values": item.int_list
            }

            pdata = json.dumps(dict)
            data.append(pdata)
            dict = {}

        return JsonResponse(
            {
                'status':message,
                'user': request.user.id,
                'payload': data
            })
            
            
            
