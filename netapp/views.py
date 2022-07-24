from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, request
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.core import serializers
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from itertools import chain


from .models import Relationship, Post, Profile, Like
from django.views.generic import TemplateView, View, UpdateView, DeleteView, ListView, DetailView
from .forms import ProfileModelForm, PostModelForm, CommentModelForm


def search_view(request):
    if request.method == "POST":
        searched = request.POST['searched']
        profiles = Profile.objects.filter(slug__contains=searched)
        return render(request, 'netapp/search.html',
                      {'searched': searched,
                       'profiles': profiles})
    else:
        return render(request, 'netapp/search.html',
                      {})


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'netapp/profile.html'
    success_url = reverse_lazy('profile-view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)

        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context["posts"] = self.get_object().get_all_authors_posts()
        context["len_posts"] = True if len(
            self.get_object().get_all_authors_posts()) > 0 else False

        return context


@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileModelForm(request.POST or None,
                            request.FILES or None, instance=profile)
    confirm = False

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            confirm = True

    context = {
        'profile': profile,
        'form': form,
        'confirm': confirm,
    }

    return render(request, 'netapp/profile.html', context)


@login_required
def invites_received_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invitations_received(profile)
    results = list(map(lambda x: x.sender, qs))
    is_empty = False
    if len(results) == 0:
        is_empty = True

    context = {
        'qs': results,
        'is_empty': is_empty,
    }

    return render(request, 'netapp/invites.html', context)


@login_required
def accept_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()

    return redirect('invites-view')


@login_required
def reject_invitation(request):
    if request.method == "POST":
        pk = request.POST.get('profile_pk')
        receiver = Profile.objects.get(user=request.user)
        sender = Profile.objects.get(pk=pk)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('invites-view')


@login_required
def invite_profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles_to_invite(user)

    context = {'qs': qs}

    return render(request, 'netapp/to_invite_list.html', context)


@login_required
def profiles_list_view(request):
    user = request.user
    qs = Profile.objects.get_all_profiles(user)

    context = {'qs': qs}

    return render(request, 'netapp/profile_list.html', context)


class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'netapp/profile_list.html'
    #context_object_name = 'qs'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=self.request.user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context["is_empty"] = False
        if len(self.get_queryset()) == 0:
            context["is_empty"] = True

        return context


@login_required
def send_invitation(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.create(
            sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profile')


@login_required
def remove_friends(request):
    if request.method == 'POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (
                Q(sender=receiver) & Q(receiver=sender))
        )
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('profile')


@login_required
def like_unlike_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_obj = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=user)

        if profile in post_obj.liked.all():
            post_obj.liked.remove(profile)
        else:
            post_obj.liked.add(profile)

        like, created = Like.objects.get_or_create(
            user=profile, post_id=post_id)

        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        else:
            like.value = 'Unlike'

            post_obj.save()
            like.save()

        data = {
            'value': like.value,
            'likes': post_obj.liked.all().count()
        }
        return JsonResponse(data, safe=False)
    return redirect('posts')


@login_required
def post_comment_create_view(request):
    qs = Post.objects.all()
    profile = Profile.objects.get(user=request.user)

    # Setting up pagination
    p = Paginator(qs, 5)
    page = request.GET.get('page')
    post_list = p.get_page(page)

    # Post form, comment form
    p_form = PostModelForm()
    c_form = CommentModelForm()
    post_added = False

    profile = Profile.objects.get(user=request.user)

    if 'submit_pForm' in request.POST:
        print(request.POST)
        p_form = PostModelForm(request.POST, request.FILES)
        if p_form.is_valid():
            instance = p_form.save(commit=False)
            instance.author = profile
            instance.save()
            p_form = PostModelForm()
            post_added = True

    if 'submit_cForm' in request.POST:
        c_form = CommentModelForm(request.POST)
        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            c_form = CommentModelForm()

    context = {
        'qs': qs,
        'profile': profile,
        'p_form': p_form,
        'c_form': c_form,
        'post_added': post_added,
        'post_list': post_list,
    }

    return render(request, 'netapp/posts.html', context)


@login_required
def posts_of_following_profiles(request):

    profile = Profile.objects.get(user=request.user)
    users = [user for user in profile.following.all()]
    posts = []
    qs = None

    for u in users:
        p = Profile.objects.get(user=u)
        p_posts = p.post_set.all()
        posts.append(p_posts)

    my_posts = profile.get_my_posts()
    posts.append(my_posts)
    if len(posts) > 0:
        my_posts = sorted(chain(*posts), reverse=True,
                          key=lambda obj: obj.created)

    # Setting up pagination
    p = Paginator(my_posts, 5)
    page = request.GET.get('page')
    post_list = p.get_page(page)

    # Post form, comment form
    p_form = PostModelForm()
    c_form = CommentModelForm()
    post_added = False

    if 'submit_pForm' in request.POST:
        print(request.POST)
        p_form = PostModelForm(request.POST, request.FILES)
        if p_form.is_valid():
            instance = p_form.save(commit=False)
            instance.author = profile
            instance.save()
            p_form = PostModelForm()
            post_added = True

    if 'submit_cForm' in request.POST:
        c_form = CommentModelForm(request.POST)
        if c_form.is_valid():
            instance = c_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get('post_id'))
            instance.save()
            c_form = CommentModelForm()

    context = {
        'posts': qs,
        'profile': profile,
        'p_form': p_form,
        'c_form': c_form,
        'post_added': post_added,
        'post_list': post_list,
    }

    return render(request, 'netapp/followers_posts.html', context)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'netapp/confirmDelete.html'
    success_url = reverse_lazy('posts')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        if not obj.author.user == self.request.user:
            messages.warning(
                self.request, 'You need to be the owner of the post in order to delete it!')
        return obj


class PostUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PostModelForm
    model = Post
    template_name = 'netapp/update.html'
    success_url = reverse_lazy('posts')

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(
                None, "You need to be the owner of the post in order to update it!")
            return super().form_invalid(form)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("posts"))
        else:
            return render(request, "netapp/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "netapp/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "netapp/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "netapp/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("all-profiles-view"))
    else:
        return render(request, "netapp/register.html")
