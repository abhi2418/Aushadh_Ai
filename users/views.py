from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser

from .serializers import (
    AuthUserRegistrationSerializer,
    AuthUserLoginSerializer,
    AuthUserListSerializer
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