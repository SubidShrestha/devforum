from django.urls import path, include, re_path
from .views import *
urlpatterns = [
    path("", PostListView.as_view(),name='home'),
    path("create/", PostCreateView.as_view(),name='post-create'),
    path("signout/", LogoutView.as_view(),name='user-logout'),
    path("detail/<int:id>", PostReplyView.as_view(),name='post-reply'),
    path("reply/<int:id>", ReplyView.as_view(),name='answer-reply'),
    path('upvote-question/',UpvoteQuestionView.as_view(),name='upvote-question'),
    path('downvote-question/',DownvoteQuestionView.as_view(),name='downvote-question'),
    path('upvote-answer/',UpvoteAnswerView.as_view(),name='upvote-answer'),
    path('downvote-answer/',DownvoteAnswerView.as_view(),name='downvote-answer'),
    path("", include("django.contrib.auth.urls")),
    path("", include("social_django.urls")),
    re_path(r'^tag-autocomplete/$',TagAutocomplete.as_view(),name='tag-autocomplete'),
]