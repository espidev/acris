from django.db import models
from django.contrib.auth.models import User


# a full group of tracks, can be owned by several users
class Collection(models.Model):
    date_created = models.DateTimeField()
    name = models.CharField(max_length=128)
    owners = models.ManyToManyField(User)
    viewers = models.ManyToManyField(User)
    is_public = models.BooleanField()


def track_path(instance, filename):
    return 'collection_{0}/tracks/{1}'.format(instance.collection.id, filename)


def track_thumbnail_path(instance, filename):
    return 'collection_{0}/track-thumbnails/{1}'.format(instance.collection.id, filename)


def playlist_thumbnail_path(instance, filename):
    return 'collection_{0}/playlists/{1}'.format(instance.collection.id, filename)


# a playlist of tracks, belonging to a collection
class Playlist(models.Model):
    date_created = models.DateTimeField()
    name = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=playlist_thumbnail_path)


# an individual music track, belonging to one collection
class Track(models.Model):
    date_uploaded = models.DateTimeField()
    name = models.CharField(max_length=128)
    file_name = models.CharField(max_length=128)
    length = models.DurationField()
    audio_format = models.CharField(max_length=128)
    artist = models.CharField(max_length=128)
    album_artist = models.CharField(max_length=128)
    album = models.CharField(max_length=128)
    genre = models.CharField(max_length=128)
    year = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    playlists = models.ManyToManyField(Playlist)
    thumbnail_src = models.ImageField(upload_to=track_thumbnail_path)
    audio_src = models.FileField("file location", upload_to=track_path)
