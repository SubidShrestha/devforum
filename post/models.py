from django.db import models
from account.models import User
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

class Question(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='question_author')
    title = models.CharField(max_length=200)
    content = RichTextUploadingField()
    tags = TaggableManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Answer(models.Model):
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name='answer_author')
    question=models.ForeignKey(Question,on_delete=models.CASCADE,related_name='question_answer')
    content=RichTextUploadingField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Reply(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name='reply_author')
    answer = models.ForeignKey(Answer,on_delete=models.CASCADE,related_name='answer_reply')
    content=RichTextUploadingField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class UpvoteQuestion(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name='upvote_question')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='upvote_user')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user','question',)

class DownvoteQuestion(models.Model):
    question = models.ForeignKey(Question,on_delete=models.CASCADE,related_name='downvote_question')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='downvote_user')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user','question',)

class UpvoteAnswer(models.Model):
    answer = models.ForeignKey(Answer,on_delete=models.CASCADE,related_name='upvote_answer')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='upvote_answer_user')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user','answer',)

class DownvoteAnswer(models.Model):
    answer = models.ForeignKey(Answer,on_delete=models.CASCADE,related_name='downvote_answer')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='downvote_answer_user')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user','answer',)