from django.contrib import admin
from .models import Post, Profile, Relationship, Comment, Like
# Register your models here.

admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Relationship)
admin.site.register(Comment)
admin.site.register(Like)
