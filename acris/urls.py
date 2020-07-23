from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
import acris.core.views as views

urlpatterns = [
    path('api/admin/', admin.site.urls),

    path('api/user/<int:user_id>/', views.UserRoute.as_view(), name='user-info'),
    path('api/user/', views.CurrentUserRoute.as_view(), name='current-user-info'),
    path('api/collections/', views.CollectionsListRoute.as_view(), name='collections'),
    path('api/collection/<int:collection_id>/', views.CollectionRoute.as_view(), name='collection-info'),
    path('api/collection/<int:collection_id>/upload/', views.CollectionUploadRoute.as_view(), name='collection-upload'),
    path('api/collection/<int:collection_id>/tracks/', views.CollectionTracksRoute.as_view(), name='collection-tracks'),
    path('api/track/<int:track_id>/', views.TrackRoute.as_view(), name='track-info'),
    path('api/collection/<int:collection_id>/playlists/', views.CollectionPlaylistsRoute.as_view(), name='collection-playlists'),
    path('api/playlist/<int:playlist_id>/', views.PlaylistRoute.as_view(), name='playlist-info'),
    path('api/playlist/<int:playlist_id>/tracks/', views.PlaylistTracksRoute.as_view(), name='playlist-tracks'),
    path('api/collection/<int:collection_id>/albums/', views.CollectionAlbumsRoute.as_view(), name='collection-albums'),
    path('api/album/<int:album_id>/', views.AlbumRoute.as_view(), name='album-info'),
    path('api/album/<int:album_id>/tracks/', views.AlbumTracksRoute.as_view(), name='collection-album-tracks'),
    path('api/collection/<int:collection_id>/artists/', views.CollectionArtistsRoute.as_view(), name='collection-artists'),
    path('api/artist/<int:artist_id>/', views.ArtistRoute.as_view(), name='artist-info'),
    path('api/artist/<int:artist_id>/tracks/', views.ArtistTracksRoute.as_view(), name='artist-tracks'),
    path('api/collection/<int:collection_id>/genres/', views.CollectionGenresRoute.as_view(), name='collection-genres'),
    path('api/genre/<str:genre_id>/', views.GenreRoute.as_view(), name='genre-info'),
    path('api/genre/<str:genre_id>/tracks/', views.GenreTracksRoute.as_view(), name='genre-tracks'),
    path('api/track/<int:track_id>/stream/', views.TrackRoute.as_view(), name='track-stream'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
