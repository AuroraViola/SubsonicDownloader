import requests
import json
import xmltodict
import os

def printSongList(songslist):
    rstr = ""
    index = 1
    for songs in songslist:
        rstr += str(index) + ". " + songs["@artist"] + " - " + songs["@album"] + "\t" + songs["@title"] + "\n"
        index += 1
    print(rstr)

def printPlaylists(playlistslist):
    rstr = ""
    index = 1
    for playlist in playlistslist:
        rstr += str(index) + ". " + playlist["@name"] + "\n"
        index += 1
    print(rstr)

def printAlbumsList(albumlist):
    rstr = ""
    index = 1
    for album in albumlist:
        rstr += str(index) + ". " + album["@artist"] + " - " + album["@name"] + "\n"
        index += 1
    print(rstr)

def getAlbumsList(par):
    par['type'] = "alphabeticalByArtist"
    par["size"] = 0
    return xmltodict.parse(requests.get(url + "getAlbumList", params=par).content)["subsonic-response"]["albumList"]["album"]

def getPlaylists(par):
    return xmltodict.parse(requests.get(url + "getPlaylists", params=par).content)["subsonic-response"]["playlists"]["playlist"]

def getSongsFromPlaylist(par):
    return xmltodict.parse(requests.get(url + "getPlaylist", params=par).content)["subsonic-response"]["playlist"]["entry"]

def downloadSong(par, path):
    songdata = xmltodict.parse(requests.get(url + "getSong", params=par).content)["subsonic-response"]["song"]
    filename = path + songdata["@track"] + ". " + songdata["@title"] + "." + songdata["@suffix"]
    data = requests.get(url + "download", params=par).content
    with open(filename, "wb") as f:
        f.write(data)

def downloadAlbum(par):
    par2 = par.copy()
    albumdata = xmltodict.parse(requests.get(url + "getAlbum", params=par).content)["subsonic-response"]["album"]
    songslist = xmltodict.parse(requests.get(url + "getAlbum", params=par).content)["subsonic-response"]["album"]["song"]
    albumpath = str(albumdata["@artist"] + " - " + albumdata["@name"])
    os.mkdir(albumpath)
    for song in songslist:
        par2["id"] = song["@id"]
        print("downloading " + song["@title"])
        downloadSong(par2, (albumpath + "/"))
    print("album download completed")

if __name__ == '__main__':
    with open("config.json", "r") as f:
        info = json.load(f)
        url = "https://" + info["hostname"] + "/rest/"
        par = {
            "u" : info["auth"]["username"],
            "p": info["auth"]["password"],
            "v": "1.16.1",
            "c": "SubsonicDownloader",
        }

    print("1. Download an entire album")
    print("2. Download a song from a playlist")
    print("Select what you want to do: ", end="")
    sel = int(input())

    if sel == 1:
        albumslist = getAlbumsList(par)
        printAlbumsList(albumslist)

        print("Select album to download: ", end="")
        albumselection = int(input())

        par["id"] = albumslist[albumselection-1]["@id"]
        downloadAlbum(par)

    elif sel == 2:
        playlistlist = getPlaylists(par)
        printPlaylists(playlistlist)

        print("Select playlist number: ", end="")
        playlistnum = int(input())
        par["id"] = playlistlist[playlistnum-1]["@id"]

        songslist = getSongsFromPlaylist(par)
        printSongList(songslist)

        print("Select song number for download: ", end="")
        songnum = int(input())
        par["id"] = songslist[songnum-1]["@id"]

        downloadSong(par, "")