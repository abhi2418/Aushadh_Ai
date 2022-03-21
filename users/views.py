from django.http import response
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser

#from .serializers import PhoneNumberSerializer
from .models import User
from django.utils import timezone
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
import pyotp
from twilio.rest import Client as TwilioClient
from decouple import config


account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config("TWILIO_AUTH_TOKEN")
twilio_phone = config("TWILIO_PHONE")
client = TwilioClient(account_sid, auth_token)
from .serializers import (
    AuthUserRegistrationSerializer,
    AuthUserLoginSerializer,
    AuthUserListSerializer,
    AuthVerifyNumber,
    AuthchangepassSerializer,
    RefreshTokenSerializer

)

from .models import User


class AuthUserRegistrationView(APIView):

    """
    this class gives access admin the permission to create users and assign them role 
    of either supervisor [2] or Operator [3]
    and supervisor can create only operator 
    whereas operator don't have access to this endpoint 
    this needs jwt access token of admin to make the request  
    """

    serializer_class = AuthUserRegistrationSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        if user.role == 3:
            response = {
                'success': False,
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'You are not authorized to perform this action'
            }
            return Response(response, status.HTTP_403_FORBIDDEN)
        else:

            serializer = self.serializer_class(data=request.data)
            valid = serializer.is_valid(raise_exception=True)
            if valid:
                if user.role == 2:
                    
                        serializer_instance = serializer.save()
                        role = 3
                        serializer_instance.role = role
                        serializer_instance.save()
                        status_code = status.HTTP_201_CREATED

                        response = {
                            'success': True,
                            'statusCode': status_code,
                            'message': 'User successfully registered!',
                            'user': serializer.data
                        }

                        return Response(response, status=status_code)
                else:
                    
                        serializer.save()
                        status_code = status.HTTP_201_CREATED

                        response = {
                            'success': True,
                            'statusCode': status_code,
                            'message': 'User successfully registered!',
                            'user': serializer.data
                        }

                        return Response(response, status=status_code)
            else:
                response={
                    'success' : False,
                    'statusCode' : status.HTTP_409_CONFLICT,
                    'message': 'Conflict while registration',
                

                }
                return Response(response, status.HTTP_409_CONFLICT)



class AuthUserLoginView(APIView):

    """ 
    to login the user which takes the jwt access token checks its validity and
    and authenticity and according to that give access to the user
    """

    serializer_class = AuthUserLoginSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'User logged in successfully',
                'access': serializer.data['access'],
                'refresh': serializer.data['refresh'],
                'authenticatedUser': {
                    'username': serializer.data['username'],
                    'role': serializer.data['role'],
                    

                }
            }

            return Response(response, status=status_code)



class AuthUserListView(APIView):
    """
    lists the users in the database this endpoint is accessed by 
    only by admin
    """
    serializer_class = AuthUserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.role != 1:
            response = {
                'success': False,
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'You are not authorized to perform this action'
            }
            return Response(response, status.HTTP_403_FORBIDDEN)
        else:
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data

            }
            return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def send_sms_code(request, format=None):
    """
    Time based OTP and setting the expiration to 500 seconds.
    """
    #Time based otp
    time_otp = pyotp.TOTP(request.user.key, interval=500)
    time_otp = time_otp.now()
    user_phone_number = request.user.phone_number #Must start with a plus '+91'
    client.messages.create(
                     body="Your verification code is "+time_otp,
                     from_=twilio_phone,
                     to=user_phone_number
                 )
    return Response(status=200)


class AuthVerifyPhone(APIView):

    """
    It takes the OTP from the url and authenticates
    the OTP if it matches then the registered number is verified
    and the verified flag from the database is set to be True
    which is then used to check if the verified user
    
    """


    serializer_class = AuthVerifyNumber
    permission_classes = (IsAuthenticated,)
    def get(self,request,sms_code, format=None):
        user = request.user
        code = int(sms_code)
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        
        if request.user.authenticate(code):
            serializer.update(user, validated_data={"verified":True})
            response = {
                'success': True,
                'status_code': status.HTTP_201_CREATED,
                'message': 'Successfully Verified the user',
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(dict(detail='The provided code did not match or has expired OR the user is not verfied'),status=200)
            


class AuthUpdatePassword(APIView):

    serializer_class = AuthUserLoginSerializer
    permission_classes = (AllowAny, )


    def get(self, request):
        """
        checks if user is verified then
        get method is used to send the OTP to verified number 
        
        """
        #serializer = self.serializer_class(data=request.data)
        if request.user.verified == True:
            #serializer.update(request.user, validated_data={"verified":True})
            time_otp = pyotp.TOTP(request.user.key, interval=300)
            time_otp = time_otp.now()
            user_phone_number = request.user.phone_number #Must start with a plus '+'
            client.messages.create(
                            body="Your verification code is "+time_otp,
                            from_=twilio_phone,
                            to=user_phone_number
                        )
            return Response(dict(detail='The code has been sent'),status=200)
        return Response(dict(detail='User not Verified'),status=200)



    def post(self, request,sms_code, format=None):
        """
        post method takes OTP as argument in the url 
        where as takes password as the body parameter 
        hashes the password and then calls the serializer to update 
        the database withh new hashed password

        """
  
        user = request.user
        code = int(sms_code)
        data = request.data
        serializer = AuthchangepassSerializer(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        
        if request.user.authenticate(code):
            #serializer.update(user, validated_data={"password":data['password']})
            user.set_password(serializer.data.get("password"))
            user.save()
            response = {
                'success': True,
                'status_code': status.HTTP_201_CREATED,
                'message': 'Successfully Changed Password',
                

            }
            return Response(response, status=status.HTTP_201_CREATED)

            
        return Response(dict(detail='The provided code did not match or has expired'),status=200)


class AuthLogoutView(APIView):
    def post(self,request,format=None):
        token = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
        print(token)
        return Response(status=status.HTTP_200_OK)


