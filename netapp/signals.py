from .models import Profile, Relationship
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

@receiver(post_save, sender=User)
def post_save_create_profile(sender, instance, created, **kwargs):
    print('sender', sender)
    print('instance', instance)
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Relationship)
def post_save_add_to_followers(sender, instance, created, **kwargs):
    sender_ = instance.sender
    receiver_ = instance.receiver
    if instance.status == 'accepted':
        sender_.following.add(receiver_.user)
        receiver_.following.add(sender_.user)
        sender_.save()
        receiver_.save()


@receiver(pre_delete, sender=Relationship)
def pre_delete_remove_from_friends(sender, instance, **kwargs):
    sender = instance.sender
    receiver = instance.receiver
    sender.following.remove(receiver.user)
    receiver.following.remove(sender.user)
    sender.save()
    receiver.save()