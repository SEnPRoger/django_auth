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

class AccountSimilar(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['nickname', 'is_verify']

class AccountGetPublic(serializers.ModelSerializer):

    subscribers_count = serializers.SerializerMethodField('get_subscribers_count')
    posts_count = serializers.SerializerMethodField('get_posts_count')

    def get_subscribers_count(self, account):
        return account.get_subcribers_count
    
    def get_posts_count(self, account):
        return account.get_posts_count

    class Meta:
        model = Account
        fields = ['username', 'nickname', 'birth_date', 'created_at', 'is_verify', 'is_blocked', 'account_photo', 'account_banner', 'city', 'country', 'biography', 'subscribers_count', 'posts_count']

class AccountGetPrivate(serializers.ModelSerializer):
    subscribers_count = serializers.SerializerMethodField('get_subscribers_count')

    def get_subscribers_count(self, account):
        return account.subscribers.count()
    
    class Meta:
        model = Account
        fields = ['username', 'nickname', 'birth_date', 'created_at', 'is_verify', 'is_blocked', 'account_photo', 'account_banner', 'city', 'country', 'biography', 'subscribers_count', 'email', 'changed_nickname']

class AccountPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()

class AccountUpdateInfoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    nickname = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    account_photo = serializers.ImageField(required=False)
    account_banner = serializers.ImageField(required=False)
    
    class Meta:
        model = Account
        fields = ['username', 'nickname', 'account_photo', 'account_banner', 'email', 'birth_date', 'biography', 'city', 'country']

class AccountVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifiedAccount
        fields = ['is_verified', 'provided_by', 'social_link']

    def create_request(self):
        request = self.context['request']
        social = request.data.get('social_link')
        return VerifiedAccount.objects.create(account=request.user, social_link=social, provided_by=None)

    def update_request(self, instance, validated_data):
        instance.is_verified = validated_data.get("is_verified")
        instance.save()

    def delete_request(self, instance):
        account = Account.objects.get(nickname=instance.account.nickname)
        account.is_verify = False
        account.save()
        instance.delete()

class AccountBlockedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['nickname', 'account_photo']