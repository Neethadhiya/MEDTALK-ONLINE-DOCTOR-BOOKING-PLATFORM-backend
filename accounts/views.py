from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import (
    UserSerializer,
    UserInfoSerializer,
    LoginSerilalizer,
    )
from rest_framework.response import Response
from .models import CustomUser,PasswordResetToken
from rest_framework.exceptions import AuthenticationFailed
import jwt,datetime
from .send_otp_to_email import send_otp_to_email
import uuid
from rest_framework import status
from .generate_otp import generate_otp
from .tokens import get_tokens
from django.contrib.auth import authenticate
from .send_otp_to_email import reset_password_send_email
from django.utils import timezone
from datetime import timedelta
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class RegisterView(APIView):
    def post(self,request):
        if not request.data:
            response_data = {
                'error' : True,
                'message' : 'No data provided'
            }
            return Response(response_data,status=400)
        email = request.data['email']
        role = request.data['role']
        if CustomUser.objects.filter(email=email,role=role).exists():
            response_data = {
                'error' : True,
                'message' : 'Email already exists'
            }
            return Response(response_data, status=400)
        mobile = request.data['mobile']
        if CustomUser.objects.filter(mobile=mobile ,role=role).exists():
            response_data = {
                'error' : True,
                'message' : 'Mobile already exists'
            }
            return Response(response_data, status=400)
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            OTP = generate_otp()
            serializer.save()
            user_instance = CustomUser.objects.get(email=serializer.data["email"])
            user_instance.otp = OTP
            user_instance.is_active = True
            user_instance.save()
            send_otp_to_email(serializer.data['email'],OTP)
            response_data = {
                    'success' : True,
                    'message' : 'OTP sent to your mail',
                }
            return Response(response_data,status=200)
        else:
            response_data = {
                    'error' : True,
                    'message' : serializer.errors,
                }
            return Response(response_data,status=400)
        
class VetifyOTP(APIView):
    def post(self,request):
        otp = request.data.get("otp")
        email = request.data['email']
        try:
            user = CustomUser.objects.get(email=email)
            if user.otp == int(otp):
                user.is_verified = True
                user.otp  = None
                user.save()
                response_data = {
                'success' : True,
                'message' : f'Your account activated..',
                }
                return  Response(response_data,status=200)
            else:
                response_data = {
                        'error' : True,
                        'message' :'Invalid OTP. Please try again'
                    }
                return Response(response_data, status = 400)
        except:
            user.delete()
            response_data = {
                    'error' : True,
                    'message' : 'Invalid OTP. Please try again',
                }
            return  Response(response_data,status=400) 
        
class LoginView(APIView):
    def post(self,request):
        if not request.data:
            response_data = {
                'error' : True,
                'message' : 'No data provided'
            }
            return Response(response_data,status=400)
        serializer = LoginSerilalizer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise AuthenticationFailed("User not found")
            if not user.check_password(password):
                response_data = {
                    'error' : True,
                    'message' : 'Password is invalid'
                }        
                return Response(response_data,status = 400)            
                       
            if user is not None:
                if user.is_active == False:
                    response_data = {
                    'error' : True,
                    'message' : 'Your account has been blocked'
                    }        
                    return Response(response_data,status = 400)
            if user.is_verified == False:
                response_data = {
                'error' : True,
                'message' : 'Your account is not verified'
                }        
                return Response(response_data,status = 400)
            user = authenticate(email = email, password = password)
            token = get_tokens(user)
            serializer = UserInfoSerializer(user)
            response_data = {
                'access_token' : token['access'],
                'refresh_token'  :token['refresh'],
                'user_info' : serializer.data, 
                'success' : True,
                'message' : 'You are successfully logged in',
            }
            return  Response(response_data,status=200)
        
class ForgotPassword(APIView):
    def post(self,request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("User not found")
        token = str(uuid.uuid4())
        expiration_time = timezone.now() + timedelta(minutes=10)
        PasswordResetToken.objects.create(email = email, token = token, expires_at = expiration_time)
        try:
            reset_password_send_email(token,email)
            response_data = {
                    'success' : True,
                    'message' : 'Reset password link has been sent to your mail',
                    }
            return  Response(response_data,status=200)
        except Exception as e:
            response_data = {
                    'error' : True,
                    'message' : 'An error occurred',
                    }
            return  Response(response_data,status=500)           

class ResetPassword(APIView):
    def post(self,request):
        if not request.data:
            response_data = {
            'error' : True,
            'message' : 'No data provided'
            }        
            return Response(response_data,status = 400)
        password = request.data.get('password')
        email = request.data.get('email')
        token = request.data.get('token')
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if reset_token.expires_at < timezone.now():
                reset_token.delete()
                response_data = {
                        'error' : True,
                        'message' : 'Your token expired..Try again',
                        }
                return  Response(response_data,status=400) 
        except PasswordResetToken.DoesNotExist:
            response_data = {
                        'error' : True,
                        'message' : 'Invalid',
                        }
            return  Response(response_data,status=400) 
        user = CustomUser.objects.get(email=email)
        user.set_password(password)
        user.save()
        response_data = {
                    'success' : True,
                    'message' : 'Your password changed successfully',
                    }
        return  Response(response_data,status=200)


        