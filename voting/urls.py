from voting.views import *
from django.urls import path, include

app_name = "voting"

urlpatterns = [
    path('add/', RetrieveUpdateDestroyPoll.as_view(), name='add_poll'),
    path('<int:id>/', RetrieveUpdateDestroyPoll.as_view(), name='get_edit_delete_poll'),
    path('choice/<int:id>/vote/', VoteCreateDelete.as_view(), name='create_delete_vote'),
]