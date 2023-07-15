from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from post.serializers import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, permission_classes
from django.db.models import Prefetch

# Create your views here.
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer = PostSerializer

    @action(methods=['post'], detail=False)
    @permission_classes([IsAuthenticated])
    def add_post(self, request, format=None):
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            post = serializer.save(author=request.user)
            response = Response({'status':'successfully posted'},
                                status=status.HTTP_200_OK)
            return response
        else:
            return Response({'status':'failed',
                         'error':serializer.errors},
                        status=status.HTTP_200_OK)
        
    @action(methods=['get'], detail=True)
    @permission_classes([AllowAny])
    def get_posts_by_author(self, request, nickname=None, format=None):
        posts = Post.objects.filter(author__nickname=nickname).order_by('-published_date')
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    @action(methods=['get'], detail=True)
    @permission_classes([AllowAny])
    def get_post_by_id(self, request, post_id=None):
        post = get_object_or_404(Post.objects.prefetch_related('reply'), id=post_id)
        serializer = PostSerializer(post, context={'request': request})

        photos = []
        for photo in serializer.data['photos']:
            file_url = photo['file']
            if file_url:
                file_url = request.build_absolute_uri(file_url)
            photos.append({'file': file_url})

        reply = []
        if post.reply is not None:
            reply_serializer = PostSerializer(post.reply, context={'request': request})
            reply.append({
                'content': reply_serializer.data['content'],
                'author_username': reply_serializer.data['author_username'],
                'author_nickname': reply_serializer.data['author_nickname'],
                'author_account_photo': reply_serializer.data['author_account_photo'],
                'published_date': reply_serializer.data['published_date'],
                'is_edited': reply_serializer.data['is_edited'],
                'device': reply_serializer.data['device'],
                'post_id': post.reply.id,
            })

        response_data = {
            'content': serializer.data['content'],
            'author_username': serializer.data['author_username'],
            'author_nickname': serializer.data['author_nickname'],
            'author_account_photo': serializer.data['author_account_photo'],
            'published_date': serializer.data['published_date'],
            'is_edited': serializer.data['is_edited'],
            'device': serializer.data['device'],
            'photos': photos,
            'reply': reply,
        }

        response = Response(response_data, status=status.HTTP_200_OK)
        return response