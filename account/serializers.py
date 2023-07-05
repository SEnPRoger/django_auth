from rest_framework import serializers
from account.models import Account, VerifiedAccount
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from rest_framework.exceptions import ParseError

class AccountRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'nickname', 'email', 'birth_date', 'account_photo', 'password']
        extra_kwargs = {
            'password' : {'write_only':True}
        }
    
    def create(self, validated_data):
        account_photo = validated_data.pop('account_photo', None)
        try:
            user = Account.objects.create_user(**validated_data)
        except ParseError:
            raise serializers.ValidationError('Invalid image file')

        if account_photo and account_photo != 'undefined':
            user.account_photo = account_photo
            user.save()

        return user
    
class AccountLoginSerializer(serializers.ModelSerializer):
    nickname_or_email = serializers.CharField(max_length=32)

    class Meta:
        model = Account
        fields = ['nickname_or_email', 'password']

class AccountGetPublic(serializers.ModelSerializer):

    subscribers_count = serializers.SerializerMethodField('get_subscribers_count')
    # posts_count = serializers.SerializerMethodField('get_posts_count')
    # photos_count = serializers.SerializerMethodField('get_photos_count')

    def get_subscribers_count(self, account):
        return account.subscribers.count()
    
    # def get_posts_count(self, account):
    #     return account.related_posts.count()
    
    # def get_photos_count(self, account):
    #     return Photo.objects.filter(author=account).count()

    class Meta:
        model = Account
        fields = ['username', 'nickname', 'birth_date', 'created_at', 'is_verify', 'is_blocked', 'account_photo', 'account_banner', 'city', 'country', 'biography', 'subscribers_count']

class AccountGetPrivate(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['nickname', 'birth_date', 'city', 'country', 'email']

class AccountPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()

class AccountUpdateInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    nickname = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    
    class Meta:
        model = Account
        fields = ['username', 'nickname', 'email', 'birth_date', 'biography', 'city', 'country']

class AccountChangeVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifiedAccount
        fields = ['is_verified']