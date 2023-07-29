from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from like.models import Like
from post.models import Post
from comment.models import Comment

# Create your views here.
class LikeView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        permission_classes = IsAuthenticated

        post_slug = self.kwargs.get('slug') or None
        comment_id = self.kwargs.get('comment_id') or None

        if post_slug is None and comment_id is None:
            return Response({'detail': 'Didn`t provide any identification parameter'}, status=status.HTTP_400_BAD_REQUEST)

        if post_slug is not None:
            post = get_object_or_404(Post, slug=post_slug)
            if request.user.is_authenticated:
                #? проверка для того чтобы нельзя было лайкнуть самого себя
                if request.user != post.author:
                    like_post = post.post_likes.filter(account=request.user).first()
                    if like_post is None:
                        like = Like.objects.create(account=request.user, post=post)
                        return Response({'detail': 'Like has been added'}, status=status.HTTP_200_OK)
                    else:
                        like_post.delete()
                        return Response({'detail': 'Like has been deleted'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'you can`t like yourself'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'please login to like'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if comment_id is not None:
            comment = get_object_or_404(Comment, id=comment_id)
            if request.user.is_authenticated:
                #? проверка для того чтобы нельзя было лайкнуть самого себя
                if request.user != comment.author:
                    like_comment = comment.comment_likes.filter(account=request.user).first()
                    if like_comment is None:
                        like = Like.objects.create(account=request.user, comment=comment)
                        return Response({'detail': 'Like has been added'}, status=status.HTTP_200_OK)
                    else:
                        like_comment.delete()
                        return Response({'detail': 'Like has been deleted'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'you can`t like yourself'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'please login to like'}, status=status.HTTP_401_UNAUTHORIZED)