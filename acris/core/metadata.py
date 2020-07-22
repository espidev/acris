import base64

import mutagen

from mutagen.flac import FLAC, Picture, error as FLACError
from mutagen.mp3 import EasyMP3, MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4

from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import datetime
from acris.core.models import Track, Album, Genre, Artist

def shared_vorbis_extract(track: Track, metadata: mutagen.FileType):
    track.length = datetime.timedelta(seconds=metadata.info.length)
    track.name = metadata.get('title')
    if metadata.get('artist') is not None:
        track.artists.add(Artist.objects.get_or_create(collection=track.collection, name=metadata.get('artist')))
    track.album_artist = metadata.get('albumartist')
    if metadata.get('album') is not None:
        track.album = Album.objects.get_or_create(collection=track.collection, name=metadata.get('album'))
    track.album_track_number = metadata.get('tracknumber')
    if metadata.get('genre') is not None:
        track.genres.add(Genre.objects.get_or_create(collection=track.collection, name=metadata.get('genre')))
    track.lyrics = metadata.get('lyrics')
    track.year = metadata.get('date')

def apply_thumbnail(track: Track, image: Image):
    image_name = str(track.id) + '.' + image.format.lower()
    track.save(image_name, InMemoryUploadedFile(image, None, image_name, Image.MIME[image.format], image.tell, None))

# extract audio file metadata and apply it onto track model
def extract_metadata(track: Track, metadata: mutagen.FileType):
    try:
        if isinstance(metadata, FLAC):
            track.audio_format = 'flac'
            shared_vorbis_extract(track, metadata)

        elif isinstance(metadata, MP3):
            # image only accessible with full ID3
            if metadata.tags.getall("APIC") is not None and len(metadata.tags.getall("APIC")) > 0:
                apply_thumbnail(track, Image.open(BytesIO(metadata.tags.getall("APIC")[0])))

            # use EasyID3 for everything else
            metadata = EasyMP3(track.audio_src)
            track.audio_format = 'mp3'
            shared_vorbis_extract(track, metadata)

        elif isinstance(metadata, MP4):
            track.name = metadata.get('\xa9nam')
            track.length = datetime.timedelta(seconds=metadata.info.length)
            track.audio_format = 'mp4'
            if metadata.get('\xa9ART') is not None:
                track.artists.add(Artist.objects.get_or_create(collection=track.collection, name=metadata.get('\xa9ART')))
            track.album_artist = metadata.get('aART')
            if metadata.get('\xa9alb') is not None:
                track.album = Album.objects.get_or_create(collection=track.collection, name=metadata.get('\xa9alb'))
            track.album_track_number = metadata['soal']
            if metadata.get('\xa9gen') is not None:
                track.genres.add(Genre.objects.get_or_create(collection=track.collection, name=metadata.get('\xa9gen')))
            track.lyrics = metadata.get('\xa9lyr')
            track.year = metadata.get('\xa9day')

            if metadata.get('covr') is not None and len(metadata.get('covr')) > 0:
                apply_thumbnail(track, Image.open(BytesIO(metadata.get('covr')[0])))

        elif isinstance(metadata, OggVorbis):
            track.audio_format = 'ogg vorbis'
            shared_vorbis_extract(track, metadata)

            for b64_data in metadata.get("metadata_block_picture", []):
                try:
                    data = base64.b64decode(b64_data)
                except (TypeError, ValueError):
                    continue
                try:
                    picture = Picture(data)
                    apply_thumbnail(track, Image.open(BytesIO(picture.data)))
                except FLACError:
                    continue
                break

        elif isinstance(metadata, OggOpus):
            track.audio_format = 'ogg opus'
            shared_vorbis_extract(track, metadata)

            for b64_data in metadata.get("metadata_block_picture", []):
                try:
                    data = base64.b64decode(b64_data)
                except (TypeError, ValueError):
                    continue
                try:
                    picture = Picture(data)
                    apply_thumbnail(track, Image.open(BytesIO(picture.data)))
                except FLACError:
                    continue
                break

    except mutagen.MutagenError:
        print("Fail :(")
