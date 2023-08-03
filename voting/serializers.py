from rest_framework import serializers
from voting.models import *
from django.db.models import Count

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['content']

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content')
        instance.save()
        return instance

class PollSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_account_photo = serializers.ImageField(source='author.account_photo', read_only=True)
    author_is_verify = serializers.BooleanField(source='author.is_verify', read_only=True)

    choices = ChoiceSerializer(many=True)

    votes_count = serializers.IntegerField()
    voted_choice = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'author_username', 'author_nickname', 'author_account_photo', 'author_is_verify', 'title', 'published_date', 'is_edited', 'choices', 'voted_choice', 'votes_count']

    def get_voted_choice(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.voted_choice
        else:
            return 'register before vote'

class PollUpdateSerializer(serializers.ModelSerializer):
    choices = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Poll
        fields = ['title', 'choices']

    def create(self, validated_data):
        request = self.context['request']
        choices_data = validated_data.pop('choices', [])
        if choices_data is not None:
            poll = Poll.objects.create(**validated_data, author=request.user)
        else:
            raise serializers.ValidationError('Any choices did not provided')

        for choice_data in choices_data:
            Choice.objects.create(poll=poll, content=choice_data)
        return poll
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')

        choices_data = validated_data.pop('choices', [])
        if choices_data is not None:
            for choice_data in choices_data:
                Choice.objects.update_or_create(poll=instance, **choice_data)

        instance.is_edited = True
        instance.save()
        return instance