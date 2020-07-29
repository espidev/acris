from django.contrib import admin

from acris.core.models import AcrisUser, Collection, Artist, Playlist, Album, Genre, Track

admin.site.register(Album)
admin.site.register(Track)
admin.site.register(Artist)
admin.site.register(Collection)
admin.site.register(Genre)
admin.site.register(Playlist)
