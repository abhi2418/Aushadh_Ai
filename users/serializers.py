
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import User

class AuthUserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'role',
            'phone_number'
        )
    
    def create(self, validated_data):
        auth_user = User.objects.create_user(**validated_data)
        return auth_user


class AuthVerifyNumber(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'verified',
        )
        sms_code = serializers.CharField(max_length=128)
        verified = serializers.BooleanField(default=False)
        def validate(self,data):
            code = data['code']
            user = authenticate(code=code)
        def update(self, instance,validated_data):
            setattr(instance, "verified", self.validated_data.get('verified', instance.verified))


class AuthchangepassSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = (
            'verified','password'
        )
        sms_code = serializers.CharField(max_length=128)
        verified = serializers.BooleanField(default=False)
        password = serializers.CharField(max_length=128, write_only=True)
        def validate(self,data):
            code = data['code']
            user = authenticate(code=code)
        def update(self, instance,validated_data):
            setattr(instance, "password", self.validated_data.get('password', instance.password))


class AuthUserLoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    sms_code = serializers.CharField(read_only=True)
    def create(self, validated_date):
        pass

    def update(self, instance, validated_data):
        if User.verified == True:
            setattr(instance, "password", self.validated_data.get('password', instance.password))

    def validate(self, data):
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid login credentials")
        
        try:
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            update_last_login(None, user)

            validation = {
                'access': access_token,
                'refresh': refresh_token,
                'username': user.username,
                'role': user.role,
                
            }

            return validation
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid login credentials")


class AuthUserListSerializer(serializers.ModelSerializer):
    """ to fetch and display the users in the DB """
    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'role',
            
        )


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': ('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
