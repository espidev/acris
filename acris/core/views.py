import os
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.http.response import HttpResponse
from django.utils.timezone import make_aware
from rest_framework import permissions, generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

import acris.core.audio as audio
import acris.core.serializers as serializers
from acris.core.models import Collection, Artist, Track, Album, Genre, Playlist
from acris.core.permissions import HasCollectionPermissionOrReadOnly


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
        return Response(serializers.CollectionViewSerializer(collections, many=True).data)

    def post(self, request, format=None):
        serializer = serializers.CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(date_created=make_aware(datetime.now()))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# route: api/collection/<collection_id>
class CollectionRoute(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, HasCollectionPermissionOrReadOnly]

    def get(self, request, collection_id, format=None):
        collection = get_collection(collection_id)
        serializer = serializers.CollectionViewSerializer(collection)
        return Response(serializer.data)

    def post(self, request, collection_id, format=None):
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
    parser_classes = (MultiPartParser,)

    def put(self, request, collection_id, format=None):
        try:
            collection = get_collection(collection_id)
            file = request.FILES['file']

            track = Track(date_uploaded=make_aware(datetime.now()), collection=collection, file_name=file.name,
                          audio_src=file)
            track.save()

            # add metadata to db
            audio.setup_track_from_file(track)
            return Response(status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
        return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


# route: api/collection/<collection_id>/tracks
class CollectionTracksRoute(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(
            serializers.TrackSerializer(Track.objects.filter(collection=kwargs['collection_id']).order_by('name'),
                                        many=True).data)


# route: api/track/<track_id>
class TrackRoute(APIView):
    serializer_class = serializers.TrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            serializer = serializers.TrackSerializer(Track.objects.get(id=kwargs['track_id']))
            return Response(serializer.data)
        except Track.DoesNotExist:
            raise Http404

    def delete(self, request, format=None, *args, **kwargs):
        Track.objects.get(id=kwargs['track_id']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# route: api/collection/<collection_id>/playlists
class CollectionPlaylistsRoute(generics.ListAPIView):
    serializer_class = serializers.PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = serializers.PlaylistSerializer(
            Playlist.objects.filter(collection=kwargs['collection_id']).order_by('name'), many=True)
        return Response(serializer.data)


# route: api/playlist/<playlist_id>
class PlaylistRoute(generics.RetrieveAPIView):
    serializer_class = serializers.PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            serializer = serializers.PlaylistSerializer(Playlist.objects.get(id=kwargs['playlist_id']))
            return Response(serializer.data)
        except Playlist.DoesNotExist:
            raise Http404


# route: api/playlist/<playlist_id>/tracks
class PlaylistTracksRoute(generics.ListAPIView):
    serializer_class = serializers.TrackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = serializers.PlaylistSerializer(
            Track.objects.filter(playlists__id=kwargs['playlist_id']).order_by('name'),
            many=True)
        return Response(serializer.data)


# route: api/collection/<collection_id>/albums
class CollectionAlbumsRoute(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        albums = Album.objects.filter(collection=kwargs['collection_id']).order_by('name')
        serializer = serializers.AlbumSerializer(albums, many=True)
        return Response(serializer.data)


# route: api/album/<album_id>
class AlbumRoute(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            serializer = serializers.AlbumSerializer(Album.objects.get(id=kwargs['album_id']))
            return Response(serializer.data)
        except Album.DoesNotExist:
            raise Http404


# route: api/album/<album_id>/tracks
class AlbumTracksRoute(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = serializers.TrackSerializer(
            Track.objects.filter(album__id=kwargs['album_id']).order_by('name'), many=True)
        return Response(serializer.data)


# route: api/collection/<collection_id>/artists
class CollectionArtistsRoute(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = serializers.ArtistSerializer(
            Artist.objects.filter(collection=kwargs['collection_id']).order_by('name'), many=True)
        return Response(serializer.data)


# route: api/artist/<artist_id>
class ArtistRoute(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            serializer = serializers.ArtistSerializer(Artist.objects.get(id=kwargs['artist_id']))
            return Response(serializer.data)
        except Artist.DoesNotExist:
            raise Http404


# route: api/artist/<artist_id>/tracks
class ArtistTracksRoute(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = serializers.TrackSerializer(
            Track.objects.filter(artists__id=kwargs['artist_id']).order_by('name'), many=True)
        return Response(serializer.data)


# route: api/collection/<collection_id>/genres
class CollectionGenresRoute(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = serializers.GenreSerializer(
            Genre.objects.filter(collection=kwargs['collection_id']).order_by('name'), many=True)
        return Response(serializer.data)


# route: api/genre/<genre_id>
class GenreRoute(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            serializer = serializers.GenreSerializer(Genre.objects.get(id=kwargs['genre_id']))
            return Response(serializer.data)
        except Genre.DoesNotExist:
            raise Http404


# route: api/genre/<genre_id>/tracks
class GenreTracksRoute(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = serializers.TrackSerializer(
            Track.objects.filter(genres__id=kwargs['genre_id']).order_by('name'), many=True)
        return Response(serializer.data)


# route: api/track/<track_id>/stream
class TrackStreamRoute(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        try:
            track = Track.objects.get(id=kwargs['track_id'])
            fsock = track.audio_src.open('rb')
            response = HttpResponse(fsock)
            response['Content-Type'] = track.audio_format
            response['Content-Disposition'] = 'attachment; filename=%s' % (track.file_name.replace(' ', '-'),)
            response['Content-Length'] = os.path.getsize(track.audio_src.path)
            response['Accept-Ranges'] = 'bytes'
            return response
        except Track.DoesNotExist:
            raise Http404
        except Exception as e:
            print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
