import base64
import io
import os
import sys

import mutagen
from django.core.files.base import ContentFile

from mutagen.flac import FLAC, Picture, error as FLACError
from mutagen.mp3 import EasyMP3, MP3
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4

from io import BytesIO
from PIL import Image
import datetime
from acris.core.models import Track, Album, Genre, Artist


def shared_vorbis_extract(track: Track, metadata: mutagen.FileType):
    # print(datetime.timedelta(seconds=metadata.info.length))
    print(metadata)  # TODO
    try:
        track.length = datetime.timedelta(seconds=metadata.info.length)

        if metadata.get('title') is not None:
            track.name = metadata.get('title')[0]

        if metadata.get('artist') is not None:
            artist, created = Artist.objects.get_or_create(collection=track.collection, name=metadata.get('artist')[0])
            track.artists.add(artist)

        if metadata.get('albumartist') is not None:
            track.album_artist = metadata.get('albumartist')[0]

        if metadata.get('album') is not None:
            track.album, created = Album.objects.get_or_create(collection=track.collection, name=metadata.get('album')[0])

        if metadata.get('tracknumber') is not None:
            track.album_track_number = metadata.get('tracknumber')[0]

        if metadata.get('genre') is not None:
            genre, created = Genre.objects.get_or_create(collection=track.collection, name=metadata.get('genre')[0])
            track.genres.add(genre)

        if metadata.get('lyrics') is not None:
            track.lyrics = metadata.get('lyrics')[0]

        if metadata.get('date') is not None:
            track.year = metadata.get('date')[0]

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)


def apply_thumbnail(track: Track, image_data):
    try:
        image = Image.open(image_data)

        output = io.BytesIO()
        image.save(output, format='JPEG')

        image_name = str(track.id) + '.png'
        track.thumbnail_src.save(image_name, ContentFile(output.getvalue()), save=True)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)


# extract audio file metadata and apply it onto track model
def extract_metadata(track: Track, metadata: mutagen.FileType):

    try:
        if isinstance(metadata, FLAC):
            track.audio_format = 'flac'
            shared_vorbis_extract(track, metadata)
            if len(metadata.pictures) > 0:
                apply_thumbnail(track, BytesIO(metadata.pictures[0].data))

        elif isinstance(metadata, MP3):
            # image only accessible with full ID3
            apic_tag_array = metadata.tags.getall('APIC')
            if apic_tag_array is not None and len(apic_tag_array) > 0:
                apply_thumbnail(track, BytesIO(apic_tag_array[0].data))

            # use EasyID3 for everything else
            metadata = EasyMP3(track.audio_src.path)
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
                    apply_thumbnail(track, BytesIO(picture.data))
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
                    apply_thumbnail(track, BytesIO(picture.data))
                except FLACError:
                    continue
                break

    except mutagen.MutagenError:
        print("Fail :(")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(e)
