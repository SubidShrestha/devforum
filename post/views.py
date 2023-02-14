from django.views.generic import View
from .models import Question
from django.contrib.auth import logout as log_out
from urllib.parse import urlencode
from django.conf import settings
from django.http import HttpResponseRedirect
from rest_framework import permissions,generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.shortcuts import redirect
from .serializers import *
from .forms import *
from dal import autocomplete
from taggit.models import Tag
from account.models import User
from account.serializers import UserSerializer
from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from utils.utils import *
from django.db.models import Q

class LogoutView(View):
    def dispatch(self, request, *args, **kwargs):
        log_out(request)
        return_to = urlencode({"returnTo": request.build_absolute_uri("/")})
        logout_url = "https://{}/v2/logout?client_id={}&{}".format(
            settings.SOCIAL_AUTH_AUTH0_DOMAIN, settings.SOCIAL_AUTH_AUTH0_KEY, return_to,
        )
        return HttpResponseRedirect(logout_url)

class PostListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'pages/home.html'
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    def get_queryset(self):
        recommended = recommend(self.request.user,Question.objects.all())
        collab_recommend_items = collab_recommend(self.request.user,UpvoteQuestion.objects.all())
        if(UpvoteQuestion.objects.filter(user=self.request.user).count() > 10):
            query = Question.objects.filter(Q(pk__in = recommended) | Q(author = self.request.user) | Q(pk__in = collab_recommend_items)).distinct()
        else:
            query = Question.objects.filter(Q(pk__in = recommended) | Q(author = self.request.user)).distinct()
        return query

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.tags.all().count() == 0:
                return redirect('select-tag')
            return super(PostListView, self).dispatch(request,*args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL)

    def get(self, request,*args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(),many=True)
        serialized_data = serializer.data
        ordered_data = sorted(serialized_data, key=lambda x:(x['created_at'],x['upvotes']),reverse=True)
        user_serializer = UserSerializer(User.objects.filter(is_superuser = False),many=True)
        return Response({"posts":ordered_data,"tags": self.request.user.tags.all(),'users':user_serializer.data},template_name=self.template_name)
    
    def post(self,request,*args, **kwargs):
        previous_url = request.META.get('HTTP_REFERER')
        data = request.POST
        search_term = data.get('search')
        if search_term is None or search_term == '':
            return redirect(previous_url)
        question = Question.objects.filter(Q(title__icontains=search_term) | Q(tags__name__icontains=search_term) | Q(author__username__icontains =search_term)).distinct()
        user = User.objects.filter(Q(username__icontains=search_term) | Q(tags__name__icontains=search_term)).distinct()
        question_serializer = self.serializer_class(question,many=True)
        ordered_data = sorted(question_serializer.data, key=lambda x:(x['created_at'],x['upvotes']),reverse=True)
        user_serializer = UserSerializer(user.filter(is_superuser=False),many=True) 
        return Response({'question_list':ordered_data,'user_list':user_serializer.data,"tags": self.request.user.tags.all()},template_name='pages/search_list.html')

class PostCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    template_name = 'pages/question.html'

    def get_queryset(self):
        query = Question.objects.filter(author = self.request.user)
        return query

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.tags.all().count() == 0:
                return redirect('select-tag')
            return super(PostCreateView, self).dispatch(request,*args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL)
    
    def get(self,request,*args, **kwargs):
        return Response({"form":PostForm(),"tags": self.request.user.tags.all()},template_name=self.template_name)

    def post(self,request,*args, **kwargs):
        new_post = PostForm(request.POST)
        title = new_post['title'].value()
        content = new_post['content'].value()
        tags = new_post['tags'].value()
        author = self.request.user
        new_question = Question.objects.create(title = title, content = content,author = author)
        tag_list = tags.split(',')
        for tag in tag_list:
            new_question.tags.add(tag)
        serializer = self.serializer_class(data=new_question)
        if serializer.is_valid():
            print(serializer.data)
            serializer.save()
        return Response({"form":PostForm(),"tags": self.request.user.tags.all()},template_name=self.template_name)

class PostReplyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    template_name = 'pages/post_threads.html'
    lookup_field = 'id'

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.tags.all().count() == 0:
                return redirect('select-tag')
            return super(PostReplyView, self).dispatch(request,*args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL)
    
    def get(self, request, *args, **kwargs):
        question = get_object_or_404(self.queryset, pk=kwargs['id'])
        serializer = self.serializer_class(question,many=False)
        return Response({'question':serializer.data,'answerform':AnswerForm(),"tags": self.request.user.tags.all()},template_name=self.template_name)
    
    def post(self,request,*args, **kwargs):
        new_answer = AnswerForm(request.POST)
        question = get_object_or_404(self.queryset, pk=kwargs['id'])
        serializer = self.serializer_class(question,many=False)
        author = self.request.user
        content = new_answer['content'].value()
        Answer.objects.create(author = author, content = content,question=question)
        return Response({'question':serializer.data,'answerform':AnswerForm(),"tags": self.request.user.tags.all()},template_name=self.template_name)

class ReplyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()
    template_name = 'pages/replies.html'
    lookup_field = 'id'

    def dispatch(self,request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            if user.tags.all().count() == 0:
                return redirect('select-tag')
            return super(ReplyView, self).dispatch(request,*args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL)
    
    def get(self, request, *args, **kwargs):
        answer = get_object_or_404(self.queryset, pk=kwargs['id'])
        serializer = self.serializer_class(answer,many=False)
        return Response({'answer':serializer.data,'replyform':ReplyForm(),"tags": self.request.user.tags.all()},template_name=self.template_name)
    
    def post(self,request,*args, **kwargs):
        new_answer = AnswerForm(request.POST)
        answer = get_object_or_404(self.queryset, pk=kwargs['id'])
        serializer = self.serializer_class(answer,many=False)
        author = self.request.user
        content = new_answer['content'].value()
        Reply.objects.create(author = author, content = content,answer=answer)
        return Response({'answer':serializer.data,'replyform':ReplyForm(),"tags": self.request.user.tags.all()},template_name=self.template_name)

@method_decorator(csrf_exempt, name='dispatch')
class UpvoteQuestionView(View):
    def post(self,request,*args, **kwargs):
        data = json.loads(request.body)
        question_id = int(data.get('content'))
        question = Question.objects.get(id = question_id)
        new_upvote,create = UpvoteQuestion.objects.get_or_create(question=question,user=self.request.user)
        if(create):
            try:
                downvote = DownvoteQuestion.objects.get(question=question,user=self.request.user)
                downvote.delete()
            except:
                pass
            return JsonResponse({'msg':'Created'},status=200)
        else:
            new_upvote.delete()
            return JsonResponse({"msg":'Already exists'},status=200)
        
@method_decorator(csrf_exempt, name='dispatch')        
class DownvoteQuestionView(View):
    def post(self,request,*args, **kwargs):
        data = json.loads(request.body)
        question_id = int(data.get('content'))
        question = Question.objects.get(id = question_id)
        new_downvote,create = DownvoteQuestion.objects.get_or_create(question=question,user=self.request.user)
        if(create):
            try:
                upvote = UpvoteQuestion.objects.get(question=question,user=self.request.user)
                upvote.delete()
            except:
                pass
            return JsonResponse({'msg':'Created'},status=200)
        else:
            new_downvote.delete()
            return JsonResponse({"msg":'Already exists'},status=200)
        
@method_decorator(csrf_exempt, name='dispatch')
class UpvoteAnswerView(View):
    def post(self,request,*args, **kwargs):
        data = json.loads(request.body)
        answer_id = int(data.get('content'))
        answer = Answer.objects.get(id = answer_id)
        new_upvote,create = UpvoteAnswer.objects.get_or_create(answer=answer,user=self.request.user)
        if(create):
            try:
                downvote = DownvoteAnswer.objects.get(answer=answer,user=self.request.user)
                downvote.delete()
            except:
                pass
            return JsonResponse({'msg':'Created'},status=200)
        else:
            new_upvote.delete()
            return JsonResponse({"msg":'Already exists'},status=200)
        
@method_decorator(csrf_exempt, name='dispatch')        
class DownvoteAnswerView(View):
    def post(self,request,*args, **kwargs):
        data = json.loads(request.body)
        answer_id = int(data.get('content'))
        answer = Answer.objects.get(id = answer_id)
        new_downvote,create = DownvoteAnswer.objects.get_or_create(answer=answer,user=self.request.user)
        if(create):
            try:
                upvote = UpvoteAnswer.objects.get(answer=answer,user=self.request.user)
                upvote.delete()
            except:
                pass
            return JsonResponse({'msg':'Created'},status=200)
        else:
            new_downvote.delete()
            return JsonResponse({"msg":'Already exists'},status=200)


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.all().order_by('slug')

        if self.q:
            qs = qs.filter(name__istartswith=self.q).order_by('slug')

        return qs

