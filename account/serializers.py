from rest_framework import serializers
from .models import User
from taggit.serializers import (TagListSerializerField,
                                TaggitSerializer)
from post.models import *
import datetime

class ReplySerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    class Meta:
        model = Reply
        fields = ["id","content","duration","answer","created_at","updated_at"]

    def get_duration(self,instance):
        duration = datetime.date.today()-instance.created_at.date()
        return duration

class UpvoteQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=UpvoteQuestion
        fields="__all__"

class DownvoteQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=DownvoteQuestion
        fields="__all__"

class UpvoteAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=UpvoteAnswer
        fields="__all__"

class DownvoteAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=DownvoteAnswer
        fields="__all__"

class AnswerSerializer(serializers.ModelSerializer):
    answer_reply = ReplySerializer(many=True,allow_null=True,read_only=True)
    duration = serializers.SerializerMethodField()
    upvote_answer = UpvoteAnswerSerializer(many=True,allow_null=True,required=False)
    downvote_answer = DownvoteAnswerSerializer(many=True,allow_null=True,required=False)
    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    class Meta:
        model = Answer
        fields = ["id","question","duration","content","answer_reply",'upvote_answer','downvote_answer','upvotes','downvotes',"created_at","updated_at"]

    def get_duration(self,instance):
        duration = datetime.date.today()-instance.created_at.date()
        return duration
    
    def get_upvotes(self,instance):
        return instance.upvote_answer.all().count()
    
    def get_downvotes(self,instance):
        return instance.downvote_answer.all().count()
    
    def get_answers(self,instance):
        return instance.answer_reply.all().count()

class PostSerializer(TaggitSerializer,serializers.ModelSerializer):
    question_answer = AnswerSerializer(many=True,allow_null=True,read_only=True)
    tags = TagListSerializerField()
    duration = serializers.SerializerMethodField()
    upvote_question = UpvoteQuestionSerializer(many=True,allow_null=True,required=False)
    downvote_question = DownvoteQuestionSerializer(many=True,allow_null=True,required=False)
    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = ['id','title','content','question_answer','answers','duration','tags','upvote_question','downvote_question','upvotes','downvotes','created_at','updated_at']
    
    def get_duration(self,instance):
        duration = datetime.date.today()-instance.created_at.date()
        return duration
    
    def get_upvotes(self,instance):
        return instance.upvote_question.all().count()
    
    def get_downvotes(self,instance):
        return instance.downvote_question.all().count()
    
    def get_answers(self,instance):
        return instance.question_answer.all().count()

class UserSerializer(TaggitSerializer,serializers.ModelSerializer):
    tags = TagListSerializerField()
    question_author = PostSerializer(many=True,read_only=True,allow_null=True)
    class Meta:
        model = User
        fields = ['id','username','tags','profile_pic','question_author','cover_pic','phone','first_name','last_name']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['question_author'] = sorted(data['question_author'],key=lambda x:x['created_at'],reverse=True)
        return data