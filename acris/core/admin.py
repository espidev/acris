from django.contrib import admin
import acris.core.models as model

# Register your models here.
admin.site.register(model.Album)
admin.site.register(model.Track)
admin.site.register(model.Artist)
admin.site.register(model.Collection)
admin.site.register(model.Genre)
admin.site.register(model.Playlist)
