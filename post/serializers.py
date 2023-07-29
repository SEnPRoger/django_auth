from rest_framework import serializers
from post.models import Post
from photo.models import Photo
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from rest_framework.exceptions import ParseError

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['file']

class PostUpdateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=600, required=False)
    is_pinned = serializers.BooleanField(required=False)

    class Meta:
        model = Post
        fields = ['content', 'is_pinned']

    def get_device(self):
        request = self.context.get('request')
        if request.user_agent.is_pc:
            return 'pc'
        elif request.user_agent.is_mobile:
            return 'mobile'
        else:
            return 'unknown'

    def create(self, validated_data, request):
        id_to_reply = None

        try:
            id_to_reply = validated_data.pop('reply_id')
        except KeyError:
            pass

        post = Post(author=request.user, **validated_data)

        if id_to_reply:
            try:
                reply = Post.objects.get(id=id_to_reply)
            except ObjectDoesNotExist:
                pass
            post.reply = reply

        post.device = self.get_device()
        post.save()

        for uploaded_file in request.FILES.getlist('photos[]'):  # Заменить на photos[] при работе с клиентом
            photo = Photo.objects.create(post=post, file=uploaded_file, author=request.user)
            photo.save()

        return post

    def update(self, instance):
        if self.validated_data.get('content') is not None:
            instance.content = self.validated_data.get('content')
        else:
            if self.validated_data.get('is_pinned') is None:
                raise ParseError
        instance.is_pinned = self.validated_data.get('is_pinned')
        instance.is_edited = True
        instance.save()
        return instance

class PostGetSerializer(serializers.ModelSerializer):
    author_id = serializers.CharField(source='author.id', read_only=True)
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_account_photo = serializers.ImageField(source='author.account_photo', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_is_verify = serializers.BooleanField(source='author.is_verify', read_only=True)

    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    
    photos = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['content', 'author_id', 'author_nickname', 'author_account_photo', 'author_username', 'author_is_verify',
                  'device', 'is_edited', 'published_date', 'slug', 'photos', 'is_liked', 'likes_count', 'comments_count',
                  'views_count', 'is_pinned']
        prefetch_related = ['photos']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.is_liked_by_user
        else:
            return 'register before like'
    
    def get_photos(self, obj):
        photos = obj.photos.all()
        photo_serializer = PhotoSerializer(photos, many=True, read_only=True)
        return photo_serializer.data