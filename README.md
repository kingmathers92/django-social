# Social Network App

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/kingmathers92/django-social-app.git
$ cd django-social-app
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python -m venv venv
$ source env/Scripts/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```

Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up by `virtualenv`.

Once `pip` has finished downloading the dependencies:

```sh
(env)$ cd project
(env)$ python manage.py runserver
```

And navigate to `http://127.0.0.1:8000/login`

### Walkthrough and motivation

One of my projects from the cs50web course with extra and work in progress features. Connected my app with fast deployment and connection to a Postgres database using [@Railway](https://railway.app/). You can create an account, post pictures or a status, follow/unfollow other users, search for other users, like/unlike users you only follow, delete and edit your own posts and comments on posts.

## To Do🔧:

- [ ] Issue with static files storage to be fixed !important
- [ ] Edit profile
- [ ] Automatically have as standard profile and background pic as soon as you create user.
- [ ] Chat feature using websocket
- [ ] Sound effects for sure
- [ ] Hashtags to browse topics(like twitter)
