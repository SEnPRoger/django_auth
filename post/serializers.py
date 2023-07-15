from rest_framework import serializers
from post.models import Post
from photo.models import Photo
from django.core.exceptions import ObjectDoesNotExist

class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_account_photo = serializers.ImageField(source='author.account_photo', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_is_verify = serializers.BooleanField(source='author.is_verify', read_only=True)
    device = serializers.CharField(read_only=True)
    published_date = serializers.DateTimeField(read_only=True)
    photos = PhotoSerializer(many=True, required=False)
    reply_id = serializers.IntegerField(required=False)

    reply_content = serializers.CharField(source='reply.content', read_only=True)
    reply_author_username = serializers.CharField(source='reply.author.username', read_only=True)
    reply_author_nickname = serializers.CharField(source='reply.author.nickname', read_only=True)
    reply_author_account_photo = serializers.ImageField(source='reply.author.account_photo', read_only=True)
    reply_author_is_verify = serializers.BooleanField(source='reply.author.is_verify', read_only=True)
    reply_published_date = serializers.DateTimeField(source='reply.published_date', read_only=True)

    id = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'is_edited', 'reply', 'reply_id', 'reply_content', 'reply_author_username', 'reply_author_nickname',
                  'reply_author_account_photo', 'reply_author_is_verify', 'reply_published_date', 'author_username', 'author_nickname',
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

        try:
            id_to_reply = validated_data.pop('reply_id')
        except KeyError:
            pass

        post = Post.objects.create(**validated_data)

        # Set the reply if id_to_reply is provided
        if id_to_reply:
            try:
                reply = Post.objects.get(id=id_to_reply)
            except ObjectDoesNotExist:
                pass
            post.reply = reply
            post.is_reply = True

        post.author = request.user
        post.device = self.get_device()

        for uploaded_file in request.FILES.getlist('photos[]'):
            photo = Photo.objects.create(file=uploaded_file, author=request.user)
            post.photos.add(photo)

        post.save()
        
        return post