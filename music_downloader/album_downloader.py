#!/usr/bin/env python3

import os
import subprocess
import urllib.request
import re
import threading


class Playlist:
    def __init__(self, url):
        self.url = url
        self.titles = []
        self.title = self.get_playlist_title()
        self.load_playlist_titles()

    def get_title(self, url, i):
        html = urllib.request.urlopen(url)
        title = re.findall(
            r"(?<=\<title\>)(.*)(?=\s\-\sYouTube)", html.read().decode("utf-8"))[0]
        #print(title)
        self.titles[i] = "\t" + str(title)

    def load_playlist_titles(self):
        html = urllib.request.urlopen(self.url)
        ids = re.findall(r"watch\?v=(\S{11})", html.read().decode("utf-8"))
        ids = list(dict.fromkeys(ids))
        threads = []
        for i, id in enumerate(ids):
            self.titles.append("")
            t = threading.Thread(target=self.get_title, args=(
                "https://www.youtube.com/watch?v=" + str(id), i,))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()

    def print_url(self):
        print(self.url)

    def get_playlist_title(self):
        html = urllib.request.urlopen(self.url)
        return re.findall(r"(?<=\<title\>)(.*)(?=\s\-\sYouTube)", html.read().decode("utf-8"))[0]

    def get_playlist(self):
        output = ""
        self.load_playlist_titles()
        output += str(self.title)
        for title in self.titles:
            output += "\n" + str(title)
        return output


class Downloader:
    def __init__(self, music_directory, artist, album):
        self.music_directory = music_directory
        self.artist = artist.title()
        self.album = album.title()
        self.search_string = str(artist) + " " + str(album)
        self.path = self.music_directory + "/" + self.artist + "/" + self.album
        self.playlists = []
        self.urls = []
        self.find_albums()
        #self.url = self.find_albums()[int(self.prompt_for_selection()) - 1]

    def find_albums(self):
        playlists = []
        search_string = str(self.search_string).replace(" ", "+")
        html = urllib.request.urlopen(
            "https://www.youtube.com/results?search_query=" + str(search_string))
        playlist_ids = re.findall(
            r"playlist\?list=(\S[^\"]+)", html.read().decode("utf-8"))
        for id in playlist_ids:
            playlists.append("https://www.youtube.com/playlist?list=" + id)
        self.urls = playlists

    def prompt_for_selection(self):
        self.load_playlists()
        i = 1
        for playlist in self.playlists:
            print(str(i) + ":\n" + playlist.get_playlist())
            i += 1
        selection = input("Enter the Number for Your Selection: ")
        return selection

    def load_playlists(self):
        print("Thinking...")
        threads = []
        for i, url in enumerate(self.urls):
            self.playlists.append("")
            t = threading.Thread(
                target=self.add_playlist, args=(url, i,))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()

    def add_playlist(self, url, i):
        self.playlists[i] = Playlist(url)

    def convert_to_mp3(self, file, track_num, artist, album):
        if "webm" in file or "m4a" in file:
            if " - " in file:
                title = str(file.split(" - ")[1]).rstrip()
            else:
                title = file.split(str(self.path) + "/")[-1]
            title = str(title.split("[")[0]).rstrip()
            command = "ffmpeg -i \"" + str(file) + "\" -metadata title=\"" + str(title) + "\" -metadata track=\"" + str(
                track_num) + "\" -metadata artist=\"" + str(artist) + "\" -metadata album=\"" + str(album) + "\" -vn -ab 128k -ar 44100 -y \"" + title + ".mp3\""
            print(command)
            os.system(command)
            print("converting " + str(file) + "...\n")
            #os.system("rm \"" + file + "\"")
            os.remove(file)

    def create_directory(self):
        os.system("mkdir -p " + self.path.replace(" ", "\ "))

    def download(self, i):
        os.chdir(self.path)
        download_command = "yt-dlp -f bestaudio --embed-metadata " + \
            self.urls[i]
        os.system(download_command)

    def convert_all(self):
        os.chdir(self.path)
        files = subprocess.check_output(
            ["ls", "-cr"]).decode("utf-8").strip().split('\n')
        threads = []
        for i, file in enumerate(files):
            t = threading.Thread(target=self.convert_to_mp3, args=(
                self.path + "/" + file, (i+1), self.artist, self.album,))
            threads.append(t)
            t.start()
        for thread in threads:
            thread.join()

    def do_the_work(self, i):
        self.create_directory()
        self.download(i)
        self.convert_all()


def check_for_dependency(dependency):
    from shutil import which
    if which(dependency) is None:
        print("Dependency \'" + str(dependency)
              + "\' is not installed and is required.\nPlease install and retry")
        quit()


def main():

    #ensure yt-dlp is installed
    check_for_dependency("yt-dlp")
    #ensure ffmpeg is installed
    check_for_dependency("ffmpeg")

    #music_directory = input("Enter Absolute Path to Music Directory: ").rstrip()
    music_directory = "/mnt/raid0/Music"
    artist = input("Enter Artist: ").rstrip()
    album = input("Enter Album: ").rstrip()
    downloader = Downloader(music_directory, artist, album)
    downloader.do_the_work()
    os.system("stty sane")
    exit()


if __name__ == "__main__":
    main()
