from rest_framework import serializers
from comment.models import Comment
from photo.models import Photo
from post.models import Post
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import get_object_or_404

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

class CommentUpdateSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField()
    reply_id = serializers.IntegerField(required=False)
    device = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = ['post_id', 'device', 'content', 'reply_id']

    def get_device(self):
        request = self.context.get('request')
        if request.user_agent.is_pc:
            return 'pc'
        elif request.user_agent.is_mobile:
            return 'mobile'
        else:
            return 'unknown'

    def create(self, validated_data):
        request = self.context['request']
        reply = None

        content = validated_data.get('content')
        
        post_id = validated_data.pop('post_id')
        post = Post.objects.get(id=post_id)
        
        id_to_reply = validated_data.pop('reply_id', None)
        if id_to_reply is not None:
            try:
                reply = Comment.objects.get(id=id_to_reply)
            except ObjectDoesNotExist:
                pass
        
        device = self.get_device()

        comment = Comment(content=content, device=device, post=post, reply=reply, author=request.user)

        for uploaded_file in request.FILES.getlist('photos[]'):
            photo = Photo.objects.create(file=uploaded_file, author=request.user)
            comment.photos.add(photo)

        comment.save()
        return comment

    def update(self, instance):
        instance.content = self.validated_data.get('content')
        instance.is_edited = True
        instance.save()
        return instance

class CommentListSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_account_photo = serializers.ImageField(source='author.account_photo', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_is_verify = serializers.BooleanField(source='author.is_verify', read_only=True)
    device = serializers.CharField(read_only=True)
    published_date = serializers.DateTimeField(read_only=True)
    
    replies_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_author_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'is_edited', 'author_nickname', 'author_account_photo', 'author_username', 'author_is_verify',
                   'published_date', 'device', 'replies_count', 'is_author_liked', 'is_liked', 'likes_count']

    def get_replies_count(self, obj):
        return obj.reply_comment_set.count()

    def get_is_author_liked(self, obj):
        author_like = obj.comment_likes.filter(account=obj.post.author)
        if author_like.exists():
            return True
        else:
            return False

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            boolean = obj.comment_likes.filter(account=request.user)
            if boolean is None:
                return False
            else:
                return True
        else:
            return 'not auth'

    def get_likes_count(self, obj):
        return obj.comment_likes.count()

class CommentSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_account_photo = serializers.ImageField(source='author.account_photo', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_is_verify = serializers.BooleanField(source='author.is_verify', read_only=True)
    device = serializers.CharField(read_only=True)
    published_date = serializers.DateTimeField(read_only=True)
    photos = PhotoSerializer(many=True, required=False)

    reply_id = serializers.IntegerField(required=False)
    post_slug = serializers.SlugField(required=False)

    reply_author_nickname = serializers.CharField(source='reply.author.nickname', read_only=True)

    id = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'is_edited', 'reply', 'reply_id', 'post_slug', 'reply_author_nickname', 'author_username', 'author_nickname',
                   'author_account_photo', 'author_is_verify', 'device', 'published_date', 'photos']

    def get_device(self):
        request = self.context.get('request')
        if request.user_agent.is_pc:
            return 'pc'
        elif request.user_agent.is_mobile:
            return 'mobile'
        else:
            return 'unknown'

    def create(self, validated_data):
        request = self.context['request']

        id_to_reply = None
        post = None

        try:
            id_to_reply = validated_data.pop('reply_id')
        except KeyError:
            pass

        post_slug = validated_data.pop('post_slug')
        post = Post.objects.get(slug=post_slug)

        comment = Comment.objects.create(post=post, **validated_data)

        # Set the reply if id_to_reply is provided
        if id_to_reply:
            try:
                reply = Comment.objects.get(id=id_to_reply)
            except ObjectDoesNotExist:
                pass
            comment.reply = reply

        comment.author = request.user
        comment.device = self.get_device()

        for uploaded_file in request.FILES.getlist('photos[]'):
            photo = Photo.objects.create(file=uploaded_file, author=request.user)
            comment.photos.add(photo)

        comment.save()
        
        return comment
