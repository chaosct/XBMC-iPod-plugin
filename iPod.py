"""
iPod for XBMC

Author: Carles F. Julia
"""

import sys
import os
import xbmc
import xbmcplugin
import xbmcgui

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( os.getcwd(), 'resources' ) )
sys.path.append (os.path.join(BASE_RESOURCE_PATH,'lib'))

import sys_utils
import os.path
import shelve
import base64

thisPlugin = None
thisPluginUrl='plugin://plugin.audio.ipod/'

ipodDB = os.path.join(BASE_RESOURCE_PATH,'data','ipodDB')

def copyInfo(mp):
    "Copy all info from iPod Database to a local file"
    import gpod
    albums = dict()
    i_itdb = gpod.itdb_parse(mp,None)
    for track in gpod.sw_get_tracks(i_itdb):
        album = track.album
        song = dict()
        song['file']=gpod.itdb_filename_on_ipod(track)
        song['title']=track.title
        song['track number']=track.track_nr
        if album not in albums:
            albums[album]=dict()
            albums[album]['title']=album
            albums[album]['songs']=list()
        albums[album]['songs'].append(song)
    pass
    d = shelve.open(ipodDB)
    d[mp]=albums
    d.close()

def MyAddDirectoryItem(url,caption,isFolder=False):
    "Helper for xbmcplugin.addDirectoryItem()"
    listItem = xbmcgui.ListItem(caption)
    xbmcplugin.addDirectoryItem(thisPlugin,url,listItem,isFolder=isFolder)

def firstLevel():
    "List the founs iPods and copy all the info"
    listipods = [m for m in sys_utils.get_mounts() if os.path.exists(os.path.join(m,'iPod_Control','iTunes','iTunesDB'))]
    for m in listipods:
        copyInfo(m)
        m64 = base64.b64encode(m)
        MyAddDirectoryItem(thisPluginUrl+m64,m,isFolder=True)
    xbmcplugin.endOfDirectory(thisPlugin)

def ListAllAlbums(url):
    mp = base64.b64decode(url)
    d = shelve.open(ipodDB)
    albums = d[mp]
    d.close()
    for a in sorted(albums):
        if a:
            a64 = base64.b64encode(a)
            MyAddDirectoryItem(thisPluginUrl+('/'.join((url,a64))),a,isFolder=True)
    xbmcplugin.endOfDirectory(thisPlugin)

def ListAllSongsFromAlbum(url):
    mp = base64.b64decode(url[0])
    album = base64.b64decode(url[1])
    d = shelve.open(ipodDB)
    albums = d[mp]
    d.close()
    for s in sorted(albums[album]['songs'],key=lambda s1: s1['track number']):
        MyAddDirectoryItem(s['file'],s['title'])
    xbmcplugin.endOfDirectory(thisPlugin)

def main(a1,a2):
    global thisPlugin
    thisPlugin = int(a2)
    try:
        url = a1
        url = url[len(thisPluginUrl):].split('/')
    except:
        url = []

    url = [u for u in url if u]

    if len(url) == 0:
        firstLevel()
    elif len(url) == 1:
        ListAllAlbums(url[0])
    elif len(url) == 2:
        ListAllSongsFromAlbum(url)

if __name__ == "__main__":
    main(sys.argv[0],sys.argv[1])

