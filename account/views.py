from rest_framework import generics, permissions
from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from dal import autocomplete
from taggit.models import Tag
from django.http import HttpResponse,JsonResponse
from .forms import TagForm
from django.shortcuts import redirect
from django.conf import settings

class UserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'
    renderer_classes = [TemplateHTMLRenderer]
    template_name='pages/userdetail.html'

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.tags.all().count() == 0:
                return redirect('select-tag')
            return super(UserView, self).dispatch(request,*args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL)
        
    def get_queryset(self):
        query = User.objects.get(username = self.kwargs['username'])
        return query
    
    def get(self,request,*args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(),many=False)
        return Response({"profile":serializer.data,"tags":serializer.data['tags']},template_name=self.template_name)

class UserProfileView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class  = UserSerializer
    queryset = User.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/profile.html'

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.tags.all().count() == 0:
                return redirect('select-tag')
            return super(UserProfileView, self).dispatch(request,*args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL)

    def get_queryset(self):
        query = User.objects.get(id = self.request.user.id)
        return query
    
    def get(self,request,*args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(),many=False)
        return Response({"profile":serializer.data,"tags":serializer.data['tags']},template_name=self.template_name)

class SelectTagView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/get_tags.html'

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.tags.all().count()==0:
                return super(SelectTagView, self).dispatch(request,*args, **kwargs)
            else:
                return redirect('home')
        else:
            return redirect(settings.LOGIN_URL)

    def get(self,request,*args, **kwargs):
        return Response({"tagform":TagForm()},template_name=self.template_name)
    
    def post(self,request,*args, **kwargs):
        new_tags = TagForm(request.POST)
        tags = new_tags['tags'].value()
        tag_list = tags.split(',')
        edit_user = User.objects.get(id=self.request.user.id)
        for tag in tag_list:
            edit_user.tags.add(tag)
        edit_user.save()
        return redirect('home')

    
class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return Tag.objects.none()

        qs = Tag.objects.all().order_by('slug')

        if self.q:
            qs = qs.filter(name__istartswith=self.q).order_by('slug')

        return qs