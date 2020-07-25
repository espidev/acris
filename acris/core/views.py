from datetime import datetime

from rest_framework import permissions, generics, mixins, status
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Q
from django.http import Http404
from django.contrib.auth.models import User
from django.utils.timezone import make_aware

import acris.core.serializers as serializers
import acris.core.audio as audio
from acris.core.models import Collection, Artist, Track, Album, Genre, Playlist
from acris.core.permissions import HasCollectionPermissionOrReadOnly, HasSubCollectionPermissionOrReadOnly


def get_collection(collection_id):
    try:
        return Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        raise Http404


# route: api/user/<user_id>
class UserRoute(APIView):
    def get(self, request, user_id, format=None):
        try:
            return Response(serializers.AcrisUserSerializer(User.objects.get(id=user_id)).data)
        except User.DoesNotExist:
            raise Http404


# route: api/user
class CurrentUserRoute(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        return Response(serializers.AcrisUserSerializer(self.request.user).data)


# route: api/collections
class CollectionsListRoute(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user
        collections = Collection.objects.filter(Q(viewers=user) | Q(owners=user))
        return Response(serializers.CollectionSerializer(collections, many=True).data)

    def post(self, request, format=None):
        serializer = serializers.CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(date_created=datetime.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# route: api/collection/<collection_id>
class CollectionRoute(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, HasCollectionPermissionOrReadOnly]

    def get(self, request, collection_id, format=None):
        collection = get_collection(collection_id)
        serializer = serializers.CollectionSerializer(collection)
        return Response(serializer.data)

    def put(self, request, collection_id, format=None):
        collection = get_collection(collection_id)
        serializer = serializers.CollectionSerializer(collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, collection_id, format=None):
        collection = get_collection(collection_id)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# route: api/collection/<collection_id>/upload
class CollectionUploadRoute(APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, collection_id, format=None):
        try:
            collection = get_collection(collection_id)
            file = request.FILES['file']

            track = Track(date_uploaded=make_aware(datetime.now()), collection=collection, file_name=file.name, audio_src=file)
            track.save()

            # add metadata to db
            audio.setup_track_from_file(track)
            return Response(status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


# route: api/collection/<collection_id>/tracks
class CollectionTracksRoute(generics.ListAPIView):
    serializer_class = serializers.TrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(get_collection(kwargs['collection_id']).track_set.all())


# route: api/track/<track_id>
class TrackRoute(APIView):
    serializer_class = serializers.TrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return Response(Track.objects.get(id=kwargs['track_id']))
        except Track.DoesNotExist:
            raise Http404

    def delete(self, request, format=None, *args, **kwargs):
        Track.objects.get(id=kwargs['track_id']).delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


# route: api/collection/<collection_id>/playlists
class CollectionPlaylistsRoute(generics.ListAPIView):
    serializer_class = serializers.PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(get_collection(kwargs['collection_id']).playlist_set.all())


# route: api/playlist/<playlist_id>
class PlaylistRoute(generics.RetrieveAPIView):
    serializer_class = serializers.PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return Response(Playlist.objects.get(id=kwargs['playlist_id']))
        except Playlist.DoesNotExist:
            raise Http404


# route: api/playlist/<playlist_id>/tracks
class PlaylistTracksRoute(generics.ListAPIView):
    serializer_class = serializers.TrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(Track.objects.filter(playlists__id=kwargs['playlist_id']))


# route: api/collection/<collection_id>/albums
class CollectionAlbumsRoute(generics.ListAPIView):
    serializer_class = serializers.AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(get_collection(kwargs['collection_id']).album_set.all())


# route: api/album/<album_id>
class AlbumRoute(generics.RetrieveAPIView):
    serializer_class = serializers.AlbumSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return Response(Album.objects.get(id=kwargs['album_id']))
        except Album.DoesNotExist:
            raise Http404


# route: api/album/<album_id>/tracks
class AlbumTracksRoute(generics.ListAPIView):
    serializer_class = serializers.TrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(Track.objects.filter(playlists__id=kwargs['album_id']))


# route: api/collection/<collection_id>/artists
class CollectionArtistsRoute(generics.ListAPIView):
    serializer_class = serializers.ArtistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(get_collection(kwargs['collection_id']).artist_set.all())


# route: api/artist/<artist_id>
class ArtistRoute(generics.RetrieveAPIView):
    serializer_class = serializers.ArtistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return Response(Artist.objects.get(id=kwargs['artist_id']))
        except Artist.DoesNotExist:
            raise Http404


# route: api/artist/<artist_id>/tracks
class ArtistTracksRoute(generics.ListAPIView):
    serializer_class = serializers.TrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(Track.objects.filter(playlists__id=kwargs['artist_id']))


# route: api/collection/<collection_id>/genres
class CollectionGenresRoute(generics.ListAPIView):
    serializer_class = serializers.GenreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(get_collection(kwargs['collection_id']).genre_set.all())


# route: api/genre/<genre_id>
class GenreRoute(generics.RetrieveAPIView):
    serializer_class = serializers.GenreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return Response(Genre.objects.get(id=kwargs['genre_set']))
        except Genre.DoesNotExist:
            raise Http404


# route: api/genre/<genre_id>/tracks
class GenreTracksRoute(generics.ListAPIView):
    serializer_class = serializers.TrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(Track.objects.filter(playlists__id=kwargs['genre_id']))


# route: api/track/<track_id>/stream
class TrackStreamRoute(APIView):
    pass
