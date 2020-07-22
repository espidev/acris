from django.db import models
from django.contrib.auth.models import AbstractUser


class AcrisUser(AbstractUser):
    description = models.TextField()


# a full group of tracks, can be owned by several users
class Collection(models.Model):
    date_created = models.DateTimeField()
    name = models.CharField(max_length=128)
    owners = models.ManyToManyField(AcrisUser, related_name='%(class)s_owners', default=[])
    viewers = models.ManyToManyField(AcrisUser, related_name='%(class)s_viewers', default=[])
    is_public = models.BooleanField()


def track_path(instance, filename):
    return 'collection-{0}/tracks/{1}'.format(instance.collection.id, filename)


def track_thumbnail_path(instance, filename):
    return 'collection-{0}/track-thumbnails/{1}'.format(instance.collection.id, filename)


def playlist_thumbnail_path(instance, filename):
    return 'collection-{0}/playlists/{1}'.format(instance.collection.id, filename)


def artist_thumbnail_path(instance, filename):
    return 'collection-{0}/artist/{1}'.format(instance.collection.id, filename)


def album_thumbnail_path(instance, filename):
    return 'collection-{0}/album/{1}'.format(instance.collection.id, filename)


def genre_thumbnail_path(instance, filename):
    return 'collection-{0}/genre/{1}'.format(instance.collection.id, filename)


# a playlist of tracks, belonging to a collection
class Playlist(models.Model):
    date_created = models.DateTimeField()
    name = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=playlist_thumbnail_path)


# an individual artist, belonging to one collection
class Artist(models.Model):
    name = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=artist_thumbnail_path)


# an individual album, belonging to one collection
class Album(models.Model):
    name = models.CharField(max_length=128)
    length = models.DurationField()
    artists = models.ManyToManyField(Artist)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=album_thumbnail_path)


# an individual genre, belonging to one collection
class Genre(models.Model):
    name = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=genre_thumbnail_path)


# an individual music track, belonging to one collection
class Track(models.Model):
    date_uploaded = models.DateTimeField()
    name = models.CharField(max_length=128)
    file_name = models.CharField(max_length=128)
    length = models.DurationField()
    audio_format = models.CharField(max_length=128)
    artists = models.ManyToManyField(Artist)
    album_artist = models.CharField(max_length=128)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    album_track_number = models.IntegerField()
    genres = models.ManyToManyField(Genre)
    lyrics = models.TextField()
    year = models.CharField(max_length=128)
    playlists = models.ManyToManyField(Playlist)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    thumbnail_src = models.ImageField(upload_to=track_thumbnail_path)
    audio_src = models.FileField("file location", upload_to=track_path)
