# Media folder scanning based on basic heuristics

## Current features
* detect movie files
* extract metadata from the filename and parent folder of movie files
* detect subtitle files related to each movie file, as well as the subtitles' language
* fetch themoviedb metadata
* rename using metadata
* remove garbage, samples, screenshots, etc
* download art, posters/backdrops
* clean database when you remove files or movies
* flatten library, every movie has its own folder
* generate a static website to browse the movie collection

## TODO
* support tv shows
* collect more metadata from themoviedb
* split scan and rename operation
* better handling of duplicate movies
* fetch subtitles
* better handling of movies that aren't found