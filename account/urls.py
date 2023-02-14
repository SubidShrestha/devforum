from django.urls import path,re_path,include
from .views import *
urlpatterns = [
    path('profile/',UserProfileView.as_view(),name = 'profile'),
    path('user/<str:username>',UserView.as_view(),name = 'user'),
    path('select-tag/',SelectTagView.as_view(),name = 'select-tag'),
    re_path(r'^tag-autocomplete/$',TagAutocomplete.as_view(),name='tag-auto'),
]
