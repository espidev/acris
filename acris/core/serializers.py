from acris.core.models import Collection, Playlist, Track, Artist, Album, Genre, AcrisUser
from rest_framework import serializers


class AcrisUserSerializer(serializers.ModelSerializer):
    # collection_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Collection.objects.all())
    class Meta:
        model = AcrisUser
        fields = ['id', 'username', 'email']


class CollectionSerializer(serializers.ModelSerializer):
    owners = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=AcrisUser.objects.all(),
    )
    viewers = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=AcrisUser.objects.all(),
    )

    class Meta:
        model = Collection
        fields = ['id', 'name', 'is_public', 'owners', 'viewers']


class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['name', 'collection']


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['name', 'collection', 'thumbnail_src']


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['name', 'length', 'artists', 'collection', 'thumbnail_src']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name', 'collection', 'thumbnail_src']


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id',
                  'date_uploaded',
                  'name',
                  'file_name',
                  'length',
                  'audio_format',
                  'artists',
                  'album_artist',
                  'album',
                  'album_track_number',
                  'genres',
                  'lyrics',
                  'year',
                  'collection',
                  'playlists',
                  'thumbnail_src']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
