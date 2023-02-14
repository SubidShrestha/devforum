from django.contrib import admin
from .models import *

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Reply)
admin.site.register(UpvoteQuestion)
admin.site.register(DownvoteQuestion)
admin.site.register(UpvoteAnswer)
admin.site.register(DownvoteAnswer)
