import mutagen
import acris.core.metadata as metadata
from acris.core.models import Track


def setup_track_from_file(track: Track):
    meta = mutagen.File(track.audio_src.path)
    metadata.extract_metadata(track, meta)
    track.save()
