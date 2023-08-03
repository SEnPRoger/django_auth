from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from voting.serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count, Case, When, Value, BooleanField, Exists, OuterRef, Subquery

# Create your views here.
class RetrieveUpdateDestroyPoll(RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollUpdateSerializer
    lookup_field = 'id'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        # queryset = Poll.objects.annotate(votes_count=Count('choices__votes'))
        # if self.request.user.is_authenticated:
        #     queryset = queryset.annotate(
        #         is_voted=Case(
        #             When(choices__votes__voted_by=self.request.user, then=Value(True)),
        #             default=Value(False),
        #             output_field=BooleanField()
        #         )
        #     )

        queryset = Poll.objects.annotate(votes_count=Count('choices__votes'))
        if self.request.user.is_authenticated:
           queryset = queryset.annotate(
                voted_choice=Subquery(
                    self.request.user.vote_set.filter(choice__poll_id=OuterRef('id')).values('choice__content')[:1]
                )
            )
        return queryset
    
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, id=self.kwargs['id'])  # Передаем 'id' в get_object_or_404
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, *args, **kwargs):
        poll = self.get_object()
        serializer = PollSerializer(poll, context=self.get_serializer_context())
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response({'detail':'poll has been added'},
                        status=status.HTTP_200_OK)
    
    def put(self, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.validated_data)
        return Response({'detail':'poll has been updated'},
                        status=status.HTTP_200_OK)
    
    def delete(self):
        instance = self.get_object()
        if instance.author == self.request.user or self.request.user.is_moderator:
            instance.delete()
            return Response({'detail':'poll has been deleted'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'detail':'you don`t have a permission'},
                            status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        permissions = []
        if self.request.method == 'PUT' or self.request.method == 'DELETE' or self.request.method == 'POST':
            permissions += [IsAuthenticated()]
        elif self.request.method == 'GET':
            permissions += [AllowAny()]
        return permissions
    
class VoteCreateDelete(CreateAPIView):
    queryset = Choice.objects.all()
    lookup_field = 'id'

    def post(self, *args, **kwargs):
        choice = self.get_object()

        # Searching for vote from current user
        vote, is_created = Vote.objects.get_or_create(choice=choice, voted_by=self.request.user)

        # If the current user already voted, delete the vote
        if not is_created:
            vote.delete()
            return Response({'detail': 'Vote has been deleted'}, status=status.HTTP_200_OK)
        # Otherwise, a new vote is created
        else:
            return Response({'detail': 'Vote has been added'}, status=status.HTTP_200_OK)