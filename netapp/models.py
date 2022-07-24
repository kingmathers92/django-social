from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from itertools import chain
import random
from django.db.models.aggregates import Max
from django.shortcuts import reverse

from django.db.models.deletion import CASCADE
from .utils import get_random_code
from django.template.defaultfilters import slugify
from django.core.validators import FileExtensionValidator
from django.db.models import Q


class ProfileManager(models.Manager):

    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(
            Q(sender=profile) | Q(receiver=profile))

        accepted = set([])
        for rel in qs:
            if rel.status == 'accepted':
                accepted.add(rel.receiver)
                accepted.add(rel.sender)
        print(accepted)

        available = [
            profile for profile in profiles if profile not in accepted]

        return available

    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles


class Profile(models.Model):
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=64, blank=True)
    avatar = models.ImageField(upload_to='avatars', default='avatar.png')
    background = models.ImageField(
        upload_to='backgrounds', default='background.png')
    following = models.ManyToManyField(
        User, related_name='following', blank=True)
    bio = models.TextField(default="No Bio..")
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    objects = ProfileManager()

    def __str__(self):
        return f"{self.user.username}"

    def get_absolute_url(self):
        return reverse("profile-view", kwargs={"slug": self.slug})

    __initial_first_name = None
    __initial_last_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial_first_name = self.first_name
        self.__initial_last_name = self.last_name

    def save(self, *args, **kwargs):
        ex = False
        to_slug = self.slug
        if self.first_name != self.__initial_first_name or self.last_name != self.__initial_last_name or self.slug == "":
            if self.first_name and self.last_name:
                to_slug = slugify(str(self.first_name) +
                                  " " + str(self.last_name))
                ex = Profile.objects.filter(slug=to_slug).exists()
                while ex:
                    to_slug = slugify(to_slug + " " + str(get_random_code()))
                    ex = Profile.objects.filter(slug=to_slug).exists()
            else:
                to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)

    def get_followers(self):
        return self.following.all()

    def get_followers_num(self):
        return self.following.all().count()

    def get_my_posts(self):
        return self.post_set.all()

    def get_country(self):
        return self.post_set.all()

    def get_following_users(self):
        following_list = [p for p in self.get_following()]
        return following_list

    def get_followers_users(self):
        following_list = [p for p in self.get_followers()]
        return following_list

    def get_all_posts(self):
        users = [user for user in self.get_following()]
        posts = []
        qs = None
        for u in users:
            p = Profile.objects.get(user=u)
            p_posts = p.post_set.all()
            posts.append(p_posts)
        my_posts = self.post_set.all()
        posts.append(my_posts)
        if len(posts) > 0:
            qs = sorted(chain(*posts), reverse=True,
                        key=lambda obj: obj.created)
        return qs

    def get_posts_num(self):
        return self.post_set.all().count()

    def get_all_authors_posts(self):
        return self.post_set.all()

    def get_likes_given_num(self):
        likes = self.like_set.all()
        total_liked = 0
        for item in likes:
            if item.value == 'Like':
                total_liked += 1
        return total_liked

    def get_likes_received_num(self):
        posts = self.post_set.all()
        total_liked = 0
        for item in posts:
            total_liked += item.all().count()
        return total_liked

    def get_proposals_for_following(self):
        profiles = Profile.objects.all().exclude(user=self.user)
        followers_list = [p for p in self.get_following()]
        available = [p.user for p in profiles if p.user not in followers_list]
        random.shuffle(available)
        return available[:3]


STATUS_CHOICES = (
    ('send', 'send'),
    ('accepted', 'accepted')
)


class RelationshipManager(models.Manager):
    def invitations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs


class Relationship(models.Model):
    sender = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"


class Post(models.Model):
    # id is created automatically by Django
    picture = models.ImageField(upload_to='images', blank=True, validators=[
                                FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    content = models.TextField()
    liked = models.ManyToManyField(Profile, blank=True, related_name="likes")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.content[:20])

    def num_likes(self):
        return self.liked.all().count()

    @property
    def like_count(self):
        return self.liked.all().count()

    def get_user_liked(self, user):
        pass

    # Number of comments
    def num_comments(self):
        return self.comment_set.all.count()


class Comment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    body = models.TextField(max_length=250)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)


LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)


class Like(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, max_length=8)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.post}-{self.value}"

    def like_numb(self):
        return self.like.all().count()
