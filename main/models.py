from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone

from cloudinary.models import CloudinaryField
from cloudinary_storage.storage import MediaCloudinaryStorage


class Artist(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя')
    photo = CloudinaryField('image', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_monthly_plays(self):
        month_ago = timezone.now() - timedelta(days=30)
        tracks = Track.objects.filter(artist=self)
        total = 0
        for track in tracks:
            total += track.plays
        return total


class Album(models.Model):
    ALBUM_TYPES = [
        ('album', 'Альбом'),
        ('single', 'Сингл'),
        ('ep', 'EP'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name='albums',
        verbose_name='Артист'
    )
    cover = CloudinaryField('image', blank=True, null=True)
    year = models.IntegerField(verbose_name='Год выпуска')
    type = models.CharField(
        max_length=10,
        choices=ALBUM_TYPES,
        default='album',
        verbose_name='Тип'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.artist.name} - {self.title}"


class Track(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    artists = models.ManyToManyField(
        Artist,
        related_name='tracks',
        verbose_name='Исполнители'
    )
    album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracks',
        verbose_name='Альбом'
    )
    track_number = models.IntegerField(default=1, verbose_name='Номер трека')

    audio_file = models.FileField(
        upload_to='tracks/',
        storage=MediaCloudinaryStorage(),
        verbose_name='Аудиофайл'
    )

    plays = models.IntegerField(default=0, verbose_name='Прослушивания')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        artists_names = ", ".join([a.name for a in self.artists.all()])
        return f"{artists_names} - {self.title}"

    def get_stream_url(self):
        return reverse('stream_audio', args=[self.audio_file.name])


class Playlist(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='playlists',
        verbose_name='Пользователь'
    )
    tracks = models.ManyToManyField(
        Track,
        blank=True,
        related_name='playlists',
        verbose_name='Треки'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track')

    def __str__(self):
        return f"{self.user.username} - {self.track.title}"


class ListeningHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listening_history'
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.CASCADE,
        related_name='listening_history'
    )
    listened_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-listened_at']
        verbose_name = 'История прослушивания'
        verbose_name_plural = 'История прослушиваний'

    def __str__(self):
        return f"{self.user.username} слушал {self.track.title} в {self.listened_at}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = CloudinaryField('image', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name='О себе')

    def __str__(self):
        return self.user.username