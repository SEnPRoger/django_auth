from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from post.serializers import *
from comment.models import Comment
from account.models import Account
from comment.serializers import CommentSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, permission_classes
from django.db.models import Prefetch
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Case, When, IntegerField, BooleanField, Value, Q
from django.db import IntegrityError
from django.contrib.auth.models import AnonymousUser
from view.models import View
from view.serializers import ViewSerializer

class PostListPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'count'
    max_page_size = 10

class PostListView(ListAPIView):
    serializer_class = PostGetSerializer
    pagination_class = PostListPagination
    kwarg_nickname = "id"
    
    def get_queryset(self):
        id = self.kwargs.get(self.kwarg_nickname)
        
        #queryset = Post.objects.filter(Q(author__pk=id) & Q(is_pinned=True)).order_by('-published_date')
        #queryset = Post.objects.filter(author__pk=id).order_by('-published_date')
        queryset = Post.objects.filter(Q(author__pk=id) & (Q(is_pinned=True) | Q(is_pinned=False))).order_by('-published_date')

        queryset = queryset.annotate(
            likes_count=Count('post_likes'),
            comments_count=Count('comments'),
            views_count=Count('views')
        )

        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_liked_by_user=Case(
                    When(post_likes__account=self.request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )

        # Оптимизация связанных таблиц photos и comments с помощью select_related и Prefetch
        queryset = queryset.select_related('author').prefetch_related(
            Prefetch('photos', queryset=Photo.objects.select_related('author'))
        ).prefetch_related(
            Prefetch('comments', queryset=Comment.objects.select_related('author'))
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class PostRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    lookup_field = "slug"

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = queryset.annotate(
            likes_count=Count('post_likes'),
            comments_count=Count('comments'),
            views_count=Count('views')
        )

        # Check if user is authenticated, and if so, add the 'is_liked_by_user' annotation
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_liked_by_user=Case(
                    When(post_likes__account=self.request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )

        return queryset

    def get(self, request, *args, **kwargs):
        permission_classes = self.get_permissions()
        post = self.get_object()

        if request.user.is_authenticated:
            view, created = post.views.get_or_create(account=request.user)
            if created:
                view_serializer = ViewSerializer(data={'account': request.user.id, 'post': post.id})
                view_serializer.is_valid(raise_exception=True)
                view_serializer.save()

        serializer = self.get_serializer(post)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            post = serializer.create(validated_data=serializer.validated_data, request=request)
        except ValueError:
            return Response({'detail':'voting title and choices must be filled'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'post has been added'}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        permission_classes = self.get_permissions()
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if request.user == post.author or request.user.is_moderator:
            try:
                serializer.update(post)
            except IntegrityError:
                return Response({'detail':'pinned post must be unique'}, status=status.HTTP_400_BAD_REQUEST)
            except ParseError:
                return Response({'detail':'post must have at least one changed field'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'detail':'post has been updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail':'you don`t have a permission'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        permission_classes = self.get_permissions()
        post = self.get_object()
        if request.user == post.author or request.user.is_moderator:
            post.photos.all().delete()
            self.perform_destroy(post)
            return Response({'detail':'post has been deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail':'you don`t have a permission'}, status=status.HTTP_403_FORBIDDEN)

    def get_serializer_class(self):
        if self.request.method == 'PUT' or self.request.method == 'PATCH' or self.request.method == 'POST':
            return PostUpdateSerializer
        elif self.request.method == 'GET' or self.request.method == 'DELETE':
            return PostGetSerializer
        return super().get_serializer_class()
        
    def get_permissions(self):
        permissions = []
        if self.request.method == 'PUT' or self.request.method == 'PATCH' or self.request.method == 'DELETE' or self.request.method == 'POST':
            permissions += [IsAuthenticated()]
        elif self.request.method == 'GET':
            permissions += [AllowAny()]
        return permissions

# Create your views here.
# class PostViewSet(ModelViewSet):
#     queryset = Post.objects.all()
#     serializer = PostSerializer

#     @action(methods=['post'], detail=False)
#     @permission_classes([IsAuthenticated])
#     def add_post(self, request, format=None):
#         serializer = PostSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid(raise_exception=True):
#             post = serializer.save(author=request.user)
#             response = Response({'status':'successfully posted'},
#                                 status=status.HTTP_200_OK)
#             return response
#         else:
#             return Response({'status':'failed',
#                          'error':serializer.errors},
#                         status=status.HTTP_200_OK)
        
#     @action(methods=['get'], detail=True)
#     @permission_classes([AllowAny])
#     def get_posts_by_author(self, request, nickname=None, format=None):
#         posts = Post.objects.filter(author__nickname=nickname).order_by('-published_date').prefetch_related(
#             Prefetch('reply', queryset=Post.objects.select_related('author'))
#         )
#         serializer = PostSerializer(posts, many=True)

#         post_obj = []
#         for post in serializer.data:

#             photos = []
#             for photo in post['photos']:
#                 file_url = photo['file']
#                 photos.append(file_url)

#             reply = post['reply']
#             reply_data = None
#             if isinstance(reply, int):
#                 # Handle the case where 'reply' is an integer (post ID)
#                 reply_post = Post.objects.get(id=reply)
#                 reply_serializer = PostSerializer(reply_post, context={'request': request})

#                 photos = []
#                 for photo in reply_serializer.data['photos']:
#                     file_url = photo['file']
#                     photos.append(file_url)

#                 reply_data = {
#                     'id': reply_serializer.data['id'],
#                     'content': reply_serializer.data['content'],
#                     'author_username': reply_serializer.data['author_username'],
#                     'author_nickname': reply_serializer.data['author_nickname'],
#                     'author_account_photo': reply_serializer.data['author_account_photo'],
#                     'author_is_verify': reply_serializer.data['author_is_verify'],
#                     'published_date': reply_serializer.data['published_date'],
#                     'is_edited': reply_serializer.data['is_edited'],
#                     'device': reply_serializer.data['device'],
#                     'photos': photos,
#                     'slug': reply_serializer.data['slug'],
#                 }
#             elif reply:
#                 # Handle the case where 'reply' is a nested object
#                 reply_data = {
#                     'id': reply['id'],
#                     'content': reply['content'],
#                     'author_username': reply['author']['username'],
#                     'author_nickname': reply['author']['nickname'],
#                     'author_account_photo': reply['author']['account_photo'],
#                     'author_is_verify': reply['author']['author_is_verify'],
#                     'published_date': reply['published_date'],
#                     'is_edited': reply['is_edited'],
#                     'device': reply['device'],
#                     'slug': reply['slug'],
#                 }

#             #comments = Comment.objects.filter(post=post)
#             #comment_serializer = CommentSerializer(comments, many=True, context={'request': request})

#             post_data = {
#                 'id': post['id'],
#                 'content': post['content'],
#                 'author_username': post['author_username'],
#                 'author_nickname': post['author_nickname'],
#                 'author_account_photo': post['author_account_photo'],
#                 'author_is_verify': post['author_is_verify'],
#                 'published_date': post['published_date'],
#                 'is_edited': post['is_edited'],
#                 'device': post['device'],
#                 'photos': photos,
#                 'reply': reply_data,
#                 'slug': post['slug'],
#                 'comments_count': post['comments_count'],
#             }
#             post_obj.append(post_data)

#         return Response(post_obj, status=status.HTTP_200_OK)
        
#     @action(methods=['get'], detail=True)
#     @permission_classes([AllowAny])
#     def get_post_by_slug(self, request, post_slug=None):
#         post = get_object_or_404(Post.objects.prefetch_related('reply'), slug=post_slug)
#         serializer = PostSerializer(post, context={'request': request})

#         photos = []
#         for photo in serializer.data['photos']:
#             file_url = photo['file']
#             photos.append(file_url)

#         reply = []
#         if post.reply is not None:
#             reply_serializer = PostSerializer(post.reply, context={'request': request})
#             reply.append({
#                 'content': reply_serializer.data['content'],
#                 'author_username': reply_serializer.data['author_username'],
#                 'author_nickname': reply_serializer.data['author_nickname'],
#                 'author_account_photo': reply_serializer.data['author_account_photo'],
#                 'author_is_verify': reply['author']['author_is_verify'],
#                 'published_date': reply_serializer.data['published_date'],
#                 'is_edited': reply_serializer.data['is_edited'],
#                 'device': reply_serializer.data['device'],
#                 'post_id': post.reply.id,
#                 'slug': reply_serializer.data['slug'],
#             })

#         comments_data = []
#         for comment in serializer.data['comments']:
#             comment_serializer = CommentSerializer(comment, context={'request': request})

#             comment_photos = []
#             for photo in comment_serializer.data['photos']:
#                 file_url = photo['file']
#                 comment_photos.append(file_url)

#             comment_obj = {
#                 'comment_id': comment_serializer.data['id'],
#                 'content': comment_serializer.data['content'],
#                 'author_nickname': comment_serializer.data['author_nickname'],
#                 'author_username': comment_serializer.data['author_username'],
#                 'author_account_photo': comment_serializer.data['author_account_photo'],
#                 'author_is_verify': comment_serializer.data['author_is_verify'],
#                 'device': comment_serializer.data['device'],
#                 'is_edited': comment_serializer.data['is_edited'],
#                 'comment_published': comment_serializer.data['published_date'],
#                 'photos': comment_photos,
#             }
#             comments_data.append(comment_obj)

#         response_data = {
#             'content': serializer.data['content'],
#             'author_username': serializer.data['author_username'],
#             'author_nickname': serializer.data['author_nickname'],
#             'author_account_photo': serializer.data['author_account_photo'],
#             'published_date': serializer.data['published_date'],
#             'is_edited': serializer.data['is_edited'],
#             'device': serializer.data['device'],
#             'photos': photos,
#             'reply': reply,
#             'slug': serializer.data['slug'],
#             'comments': comments_data,
#         }

#         response = Response(response_data, status=status.HTTP_200_OK)
#         return response
    
#     @action(methods=['delete'], detail=True)
#     @permission_classes([IsAuthenticated])
#     def remove_post(self, request, post_slug=None, format=None):
#         post = get_object_or_404(Post, slug=post_slug)
#         if request.user.is_moderator or post.author.nickname == request.user.nickname:
#             post.delete()
#             response = Response({'status':'post successfully deleted'},
#                                         status=status.HTTP_200_OK)
#             return response
#         else:
#             response = Response({'status':'you don`t have a permission to delete this post'},
#                                     status=status.HTTP_200_OK)
#             return response

