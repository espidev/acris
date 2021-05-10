## Acris 
##### An open source music aggregation server

A simple Django based service that exposes a basic REST API that allows users to manage and stream from multiple music collections.

The reference (React based) UI implementation is [acris-web](https://github.com/espidev/acris-web).

### Endpoints

```
api/user/<user_id>                         - user information
api/user                                   - current user
api/collections                            - list user collections
api/collection/<collection_id>             - collection information
api/collection/<collection_id>/upload      - upload to collection
api/collection/<collection_id>/tracks      - collection tracklist
api/collection/<collection_id>/playlists   - collection playlists
api/collection/<collection_id>/albums      - collection albums
api/collection/<collection_id>/artists     - collection artists
api/collection/<collection_id>/genres      - collection genres
api/track/<track_id>                       - track information
api/track/<track_id>/stream                - stream audio for track
api/playlist/<playlist_id>                 - playlist information
api/playlist/<playlist_id>/tracks          - playlist tracklist
api/album/<album_id>                       - album information
api/album/<album_id>/tracks                - album tracklist
api/artist/<artist_id>                     - artist information
api/artist/<artist_id>/tracks              - artist tracklist
api/genre/<genre_id>                       - genre information
api/genre/<genre_id>/tracks                - genre tracklist
```

### Future Plans

Create a native mobile application for in [Kirigami](https://invent.kde.org/frameworks/kirigami) for [Plasma Mobile](https://www.plasma-mobile.org/) and other mobile linux environments. 
