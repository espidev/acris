"""acris URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/user/<int:user_id>', name='user-info'),
    path('api/collections', name='collections'),
    path('api/collection/<int:collection_id>', name='collection-info'),
    path('api/collection/<int:collection_id>/tracks', name='collection-tracks'),
    path('api/collection/<int:collection_id>/playlists', name='collection-playlists'),
    path('api/collection/<int:collection_id>/albums', name='collection-albums'),
    path('api/collection/<int:collection_id>/album/<str:album>', name='collection-album-tracks'),
    path('api/collection/<int:collection_id>/artists', name='collection-artists'),
    path('api/collection/<int:collection_id>/artist/<str:artist>', name='collection-artist-tracks'),
    path('api/collection/<int:collection_id>/album-artists', name='collection-album-artists'),
    path('api/collection/<int:collection_id>/album-artist/<str:album_artist>', name='collection-album-artist-tracks'),
    path('api/collection/<int:collection_id>/genres', name='collection-genres'),
    path('api/collection/<int:collection_id>/genre/<str:genre>', name='collection-genre-tracks'),
    path('api/playlist/<int:playlist_id>', name='playlist-info'),
    path('api/track/<int:track_id>', name='track-info'),
    path('api/track/<int:track_id>/stream', name='track-stream'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
] + settings.urls.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
