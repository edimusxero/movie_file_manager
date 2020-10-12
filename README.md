# movie_file_manager
Script I use for managing my Plex libraries

This script probably has no use for any one else but I wanted to have examples of my work in my repositoy.  This script basically checks a folder in which couchpotato uses to move completed movie downloads to.  These files are renamed by couchpotato but could also be renamed manually using FileBot.

Once the files have been renamed this script first checks the file using TMDB API to determine the release language of the film.  My current Plex set up is broken into 2 libraries, Standard movies and Foreign releases.  

Based on the language returned the script then checks for the existence of the movie is either library and acts based on the results.  I prefer to keep smaller file sizes and MP4 files in my libraries so if the movies exists but the new file is an MP4 and the existing is not (or if the existing is an MP4 but is larger) it will be replaced.  

Since I do not use a flat file system with my libraries (for Radarr integration) it must also create the proper folder before moving the movies to the library.

I do not plan on spending any more time on this script nor do I plan on updating it very ofter, this is solely for an example of my work.
