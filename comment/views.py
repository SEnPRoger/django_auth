from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, permission_classes
from rest_framework import status
from comment.serializers import *
from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from post.models import Post

# Create your views here.
class CommentRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    serializer_class = CommentUpdateSerializer

    def post(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status':'successfully commented'}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        comment = self.get_object()
        serializer = serializer_class(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if request.user == comment.author or request.user.is_moderator:
            serializer.update(comment)
            return Response({'detail':'comment has been updated'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail':'you don`t have permission'}, status=status.HTTP_403_FORBIDDEN)
        
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user == comment.author or request.user.is_moderator:
            comment.photos.all().delete()
            self.perform_destroy(comment)
            return Response({'detail':'comment has been deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail':'you don`t have a permission'}, status=status.HTTP_403_FORBIDDEN)

class CommentListPaggination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'count'
    max_page_size = 10

class CommentListView(ListAPIView):
    serializer_class = CommentListSerializer
    pagination_class = CommentListPaggination
    kwarg_post = 'post_slug'
    kwarg_replies = 'comment_replies_id'
    kwarg_sort = 'sorting_method'

    def get_queryset(self):
        slug = self.kwargs.get(self.kwarg_post)
        if slug is None:
            comment_replies_id = self.kwargs.get(self.kwarg_replies)
            comment = get_object_or_404(Comment, id=comment_replies_id)
            comments = comment.reply_comment_set.all().order_by('-published_date')
        else:
            post = get_object_or_404(Post, slug=slug)
            comments = post.comments.all().order_by(self.get_sorting_method())
        return comments
    
    def get_sorting_method(self):
        sort = self.kwargs.get(self.kwarg_sort)
        if sort == 'newest':
            return '-published_date'
        elif sort == 'oldest':
            return 'published_date'
        elif sort is None:
            return '-published_date'
        