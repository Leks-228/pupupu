from django.contrib import admin
from .models import Artist, Album, Track, Playlist

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'year', 'type', 'track_count')
    list_filter = ('artist', 'type', 'year')
    search_fields = ('title', 'artist__name')
    
    def track_count(self, obj):
        return obj.tracks.count()
    track_count.short_description = 'Треков'

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist_names', 'album', 'track_number', 'plays')
    list_filter = ('artists', 'album')
    search_fields = ('title', 'artists__name')
    filter_horizontal = ('artists',)
    
    def artist_names(self, obj):
        return ", ".join([a.name for a in obj.artists.all()])
    artist_names.short_description = 'Исполнители'

admin.site.register(Playlist)