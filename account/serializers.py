from rest_framework import serializers
from account.models import Account
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from rest_framework.exceptions import ParseError

class AccountRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['username', 'nickname', 'email', 'account_photo', 'password', 'password2']
        extra_kwargs = {
            'password' : {'write_only':True}
        }
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError('Both passwords should be equal')
        return attrs
    
    def create(self, validated_data):
        account_photo = validated_data.pop('account_photo', None)
        try:
            user = Account.objects.create_user(**validated_data)
        except ParseError:
            raise serializers.ValidationError('Invalid image file')

        if account_photo:
            user.account_photo = account_photo
            user.save()

        return user
    
class AccountLoginSerializer(serializers.ModelSerializer):
    nickname_or_email = serializers.CharField(max_length=32)

    class Meta:
        model = Account
        fields = ['nickname_or_email', 'password']