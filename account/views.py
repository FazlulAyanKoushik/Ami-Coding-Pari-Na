from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .serializers import *
from django.contrib import auth
from rest_framework.renderers import JSONRenderer
import json
from django.http import HttpResponse
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from .utils import Utils
import jwt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# manually create a token for a user.
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(GenericAPIView):
    def get(self, request, format=None):
        return render(request, 'registration/register.html')
    
    serializer_class = UserRegistrationSerializer
    renderer_classes = [UserRenderer]
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)

            # send mail with token
            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])
            access_token = token['access']
            current_site = get_current_site(request).domain
            relativeLink = reverse('email-verify')
            activate_url = 'http://'+current_site+relativeLink+'?token='+str(access_token)
            
            email_subject = 'Activate your acctount'
            email_body = 'Hi '+user.name+'\nPlease use the link below to verify your email address to activate your ERP account\n'+activate_url
            sender_email = settings.EMAIL_HOST_USER
            receiver_email = user.email
            
            data = {
                'domain':activate_url,
                'email_subject':email_subject,
                'email_body':email_body,
                'sender_email':sender_email,
                'receiver_email':receiver_email
            }
            
            Utils.send_email(data)
            
            return Response(
                {
                    'user':user_data,
                    'token':token,
                    'message': 'Registration Successful'
                },status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        
class UserLoginView(GenericAPIView):
    def get(self, request, format=None):
        return render(request, 'registration/login.html')
        
    serializer_class = UserLoginSerializer
    renderer_classes = [UserRenderer]
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            
            user_obj = User.objects.get(email=email)
            if not user_obj.is_verified and not user.is_active:
                return Response(
                    {
                        'message':'Please check your email and activate your account'
                    },status=status.HTTP_400_BAD_REQUEST)
            user = auth.authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                auth.login(request, user)
                user_serializer = UserSerializer(user_obj)
                
                return Response(
                    {
                        'user': user_serializer.data,
                        'token': token,
                        'message':'Login Successful',
                        'redirect': True,
                    },status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'message':'Email or Password is not valid'
                    },status=status.HTTP_404_NOT_FOUND)
        return Response({'message: serializer.errors'}, status=status.HTTP_400_BAD_REQUEST)   
    
    
class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
    
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request, format=None):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return redirect('login')
                # return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)      
        
    