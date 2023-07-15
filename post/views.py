from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from post.serializers import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404

# Create your views here.
class AddPost(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
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
        
    permission_classes = [AllowAny]
    def get(self, request, post_id=None):
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

        response = Response({'detail': response_data},
                            status=status.HTTP_200_OK)
        return response