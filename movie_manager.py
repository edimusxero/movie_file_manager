#!/usr/local/bin/python3.8
import os
import re
import shutil
import threading
import time
import sys
import configparser
import os.path
import tmdbsimple as tmdb

from colorama import Fore, Back, Style


config = configparser.ConfigParser()
config.read('<path to my config.ini>')

tmdb.API_KEY = config['movie']['API']
search = tmdb.Search()

mypath = config['movie']['path']
orig_eng = config['movie']['orig_eng']
english_movies = config['movie']['english_movies']
foreign_movies = config['movie']['foreign_movies']


def getPERCECENTprogress(source_path, destination_path):
    time.sleep(.24)
    if os.path.exists(destination_path):
        while os.path.getsize(source_path) != \
                 os.path.getsize(destination_path):
            sys.stdout.write('\r')
            percentagem = int((float(os.path.getsize(destination_path)) /
                              float(os.path.getsize(source_path))) * 100)
            steps = int(percentagem/5)
            copiado = int(os.path.getsize(destination_path)/1000000)
            sizzz = int(os.path.getsize(source_path)/1000000)
            sys.stdout.write(("{:d} / {:d} Mb   ".format(copiado, sizzz))
                             + (Style.BRIGHT + Fore.MAGENTA + "{:20s}".format
                                 ('|'*steps) + Style.RESET_ALL)
                             + ("   {:d}% ".format(percentagem)))
            sys.stdout.flush()
            time.sleep(.01)


def CPprogress(SOURCE, DESTINATION):
    if os.path.isdir(DESTINATION):
        dst_file = os.path.join(DESTINATION, os.path.basename(SOURCE))
    else:
        dst_file = DESTINATION
    print(Style.BRIGHT + Fore.WHITE
          + "FROM : " + Fore.YELLOW
          + SOURCE + Style.RESET_ALL)
    print(Style.BRIGHT + Fore.WHITE
          + "TO   : " + Fore.YELLOW
          + dst_file + Style.RESET_ALL + "\n")
    threading.Thread(name='progresso',
                     target=getPERCECENTprogress,
                     args=(SOURCE, dst_file)).start()
    shutil.copy2(SOURCE, DESTINATION)
    os.chmod(dst_file, 0o777)
    time.sleep(.01)
    sys.stdout.write('\r')
    sys.stdout.write(("         {:d} / {:d} Mb   ".format
                     ((int(os.path.getsize(dst_file)/1000000)),
                      (int(os.path.getsize(SOURCE)/1000000))))
                     + (Style.BRIGHT + Fore.GREEN
                     + "{:20s}".format('|'*20)
                     + Style.RESET_ALL)
                     + ("   {:d}% ".format(100)))
    sys.stdout.flush()
    print("\n\n")
    time.sleep(1)
    os.remove(SOURCE)


def getSize(file_to_check):
    statinfo = os.stat(file_to_check)
    return(statinfo.st_size)


def setLanguage(language):
    if(language == 'en'):
        return(orig_eng, english_movies)
    else:
        return([foreign_movies])


def checkfolder(movie, src_size, language):
    for folder_origin in setLanguage(language):
        folder_name = os.path.splitext(os.path.basename(movie))[0]
        full_path = os.path.join(folder_origin, folder_name)
        if(os.path.isdir(os.path.join(folder_origin, folder_name))):
            if os.path.isfile(os.path.join(full_path, movie)):
                print(Fore.RED + "Movie " + Back.WHITE
                      + movie + Back.RESET
                      + " exists! Removing!"
                      + Style.RESET_ALL + "\n")
                remove = os.path.join(mypath, movie)
                os.remove(remove)
            else:
                if len(os.listdir(full_path)) == 0:
                    print(Fore.RED + "Empty Folder "
                          + Back.WHITE + movie
                          + Back.RESET + Style.RESET_ALL + "\n")
                    CPprogress(os.path.join(mypath, movie), full_path)
                else:
                    for mv in os.listdir(full_path):
                        x, ext = os.path.splitext(mv)
                        if(ext in {'.sub',
                                   '.sv2',
                                   '.subviewer2',
                                   '.sami',
                                   '.txt',
                                   '.nfo'}):
                            continue
                        else:
                            if (movie.endswith('.srt') or ext == '.srt'):
                                CPprogress(os.path.join(mypath, movie),
                                           full_path)
                            else:
                                existing_size = getSize(os.path.join
                                                        (full_path, mv))
                                if(int(src_size) < int(existing_size)):
                                    print(Fore.RED + "New Movie File "
                                          + Back.WHITE + movie
                                          + Back.RESET
                                          + " is Smaller! Replacing \
                                          Existing With Smaller Version!"
                                          + Style.RESET_ALL + "\n")
                                    remove = os.path.join(full_path, mv)
                                    os.remove(remove)
                                    CPprogress(os.path.join
                                               (mypath, movie), full_path)
                                elif(ext not in {'.mp4'} and
                                     os.path.splitext(movie)[1]
                                     in {'.mp4'}):
                                    print(Fore.RED + "New Movie File "
                                          + Back.WHITE + movie
                                          + Back.RESET + " is an MP4 and \
                                          I prefer that! Replacing : "
                                          + Style.RESET_ALL + mv + "\n")
                                    remove = os.path.join(full_path, mv)
                                    os.remove(remove)
                                    CPprogress(os.path.join
                                               (mypath, movie), full_path)
                                else:
                                    CPprogress(os.path.join
                                               (mypath, movie), full_path)

        else:
            if(str(folder_origin) != str(orig_eng)):
                new_folder = os.path.join(folder_origin, folder_name)
                os.umask(0)
                os.makedirs(new_folder, mode=0o777)
                CPprogress(os.path.join(mypath, movie), full_path)


def find_this(movie_name):
    nm = re.search(r'^(.+?) \((\d+)\)\..+$', movie_name)
    title_cleaned = nm[1]
    movie_year = nm[2]

    search.movie(query=title_cleaned, year=movie_year)

    for res in search.results:
        try:
            match_year, m, d = res['release_date'].split('-')
        finally:
            match_year = '0000'

        stripped_title = res['title'].replace(':', '')
        if(stripped_title == title_cleaned and match_year == movie_year):
            return(res['original_language'])


for movie_name in sorted(os.listdir(mypath)):
    if os.path.isfile(os.path.join(mypath, movie_name)):
        if re.search(r'^.*\.srt.random.*$|^.+\.jpg$', movie_name):
            print(Fore.CYAN + "Deleteing Junk File!" + Style.RESET_ALL + "\n")
            remove = os.path.join(mypath, movie_name)
            os.remove(remove)
            continue
        else:
            language = find_this(movie_name)
            try:
                source = os.path.join(mypath, movie_name)
                checkfolder(movie_name, getSize(source), language)
            finally:
                pass
