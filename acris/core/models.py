import os
from datetime import timedelta

from django.db import models
from django.dispatch import receiver

from django.contrib.auth.models import AbstractUser


def delete_file_on_change_helper(old_file, new_file):
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


def delete_file_on_delete_helper(file_field):
    if file_field:
        if os.path.isfile(file_field.path):
            os.remove(file_field.path)


# ~~~ User ~~~

class AcrisUser(AbstractUser):
    description = models.TextField()


# ~~~ Collection ~~~
# a full group of tracks, can be owned by several users
class Collection(models.Model):
    date_created = models.DateTimeField()
    name = models.CharField(max_length=128)
    owners = models.ManyToManyField(AcrisUser, related_name='%(class)s_owners', default=[])
    viewers = models.ManyToManyField(AcrisUser, related_name='%(class)s_viewers', default=[])
    is_public = models.BooleanField()


# ~~~ Artist ~~~
def artist_thumbnail_path(instance, filename):
    return 'collection-{0}/artist/{1}'.format(instance.collection.id, filename)


# an individual artist, belonging to one collection
class Artist(models.Model):
    name = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=artist_thumbnail_path)


@receiver(models.signals.post_delete, sender=Artist)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    delete_file_on_delete_helper(instance.thumbnail_src)


@receiver(models.signals.pre_save, sender=Artist)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_obj = Track.objects.get(pk=instance.pk)
        delete_file_on_change_helper(old_obj.thumbnail_src, instance.thumbnail_src)
    except Artist.DoesNotExist:
        return False


# ~~~ Album ~~~
def album_thumbnail_path(instance, filename):
    return 'collection-{0}/album/{1}'.format(instance.collection.id, filename)


# an individual album, belonging to one collection
class Album(models.Model):
    name = models.CharField(max_length=128)
    length = models.DurationField(default=timedelta(seconds=0))
    artists = models.ManyToManyField(Artist, default=[])
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=album_thumbnail_path)


@receiver(models.signals.post_delete, sender=Album)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    delete_file_on_delete_helper(instance.thumbnail_src)


@receiver(models.signals.pre_save, sender=Album)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_obj = Track.objects.get(pk=instance.pk)
        delete_file_on_change_helper(old_obj.thumbnail_src, instance.thumbnail_src)
    except Album.DoesNotExist:
        return False


# ~~~ Genre ~~~
def genre_thumbnail_path(instance, filename):
    return 'collection-{0}/genre/{1}'.format(instance.collection.id, filename)


# an individual genre, belonging to one collection
class Genre(models.Model):
    name = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=genre_thumbnail_path)


@receiver(models.signals.post_delete, sender=Genre)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    delete_file_on_delete_helper(instance.thumbnail_src)


@receiver(models.signals.pre_save, sender=Genre)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_obj = Track.objects.get(pk=instance.pk)
        delete_file_on_change_helper(old_obj.thumbnail_src, instance.thumbnail_src)
    except Genre.DoesNotExist:
        return False


# ~~~ Playlist ~~~
def playlist_thumbnail_path(instance, filename):
    return 'collection-{0}/playlists/{1}'.format(instance.collection.id, filename)


# a playlist of tracks, belonging to a collection
class Playlist(models.Model):
    date_created = models.DateTimeField()
    name = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=playlist_thumbnail_path)


# ~~~ Track ~~~
def track_path(instance, filename):
    return 'collection-{0}/tracks/{1}'.format(instance.collection.id, filename)


def track_thumbnail_path(instance, filename):
    return 'collection-{0}/track-thumbnails/{1}'.format(instance.collection.id, filename)


# an individual music track, belonging to one collection
class Track(models.Model):
    date_uploaded = models.DateTimeField()
    name = models.CharField(max_length=128)
    file_name = models.CharField(max_length=128)
    length = models.DurationField(null=True)
    audio_format = models.CharField(max_length=128, default='Unknown')
    artists = models.ManyToManyField(Artist)
    album_artist = models.CharField(max_length=128, default='Unknown')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)
    album_track_number = models.IntegerField(default=0)
    genres = models.ManyToManyField(Genre)
    lyrics = models.TextField(default='')
    year = models.CharField(max_length=128, null=True)
    playlists = models.ManyToManyField(Playlist)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField("thumbnail location", upload_to=track_thumbnail_path)
    audio_src = models.FileField("file location", upload_to=track_path)

    # def save(self, *args, **kwargs):
    #     self.artists_display = ''
    #     self.genres_display = ''
    #
    #     # update display strings
    #     for ind, artist in enumerate(self.artists.order_by('name')):
    #         if ind == 0:
    #             self.artists_display = artist.name
    #         else:
    #             self.artists_display += ' & ' + artist.name
    #
    #     for ind, genre in enumerate(self.genres.order_by('name')):
    #         if ind == 0:
    #             self.genres_display = genre.name
    #         else:
    #             self.genres_display += ', ' + genre.name
    #
    #     super(Track, self).save(*args, **kwargs)


@receiver(models.signals.pre_delete, sender=Track)
def pre_delete_track(sender, instance, **kwargs):
    for artist in instance.artists:
        if artist.track_set.count() == 1:
            artist.delete()

    for genre in instance.genres:
        if genre.track_set.count() == 1:
            genre.delete()


@receiver(models.signals.post_delete, sender=Track)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    delete_file_on_delete_helper(instance.audio_src)
    delete_file_on_delete_helper(instance.thumbnail_src)


@receiver(models.signals.pre_save, sender=Track)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_obj = Track.objects.get(pk=instance.pk)
        delete_file_on_change_helper(old_obj.audio_src, instance.audio_src)
        delete_file_on_change_helper(old_obj.thumbnail_src, instance.thumbnail_src)
    except Track.DoesNotExist:
        return False
