from rest_framework import serializers
from post.models import Post

class PostSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_account_photo = serializers.ImageField(source='author.account_photo', read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    device = serializers.CharField(read_only=True)
    published_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        fields = ['content', 'is_edited', 'reply', 'author_username', 'author_nickname', 'author_account_photo', 'device', 'published_date']

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
        try:
            id_to_reply = validated_data.pop('reply')
        except KeyError:
            pass

        post = Post.objects.create(**validated_data)

        # Set the reply if id_to_reply is provided
        if id_to_reply:
            post.reply = Post.objects.get(id=id_to_reply)
            post.is_reply = True

        post.author = request.user
        post.device = self.get_device()
        post.save()
        
        return post