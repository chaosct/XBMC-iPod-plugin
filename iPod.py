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

def isUrl(name):
    def register(f):
        global urls_views
        try:
            urls_views
        except NameError:
            urls_views = dict()
        urls_views[name]=f
        return f
    return register

def call_Url(u):
    global urls_views
    try:
        url = u
        url = url[len(thisPluginUrl):].split('/')
    except:
        url = ['']
    view = url[0]
    args = url[1:]
    
    if not view or view not in urls_views:
        view = 'list_ipods'
        args = []
    
    args = [base64.b64decode(a) for a in args if a]
    
    f = urls_views[view]
    f(*args)

def make_Url(f,*args):
    #global urls_views_inverse
    #try:
    #    urls_views_inverse
    #except:
    urls_views_inverse = dict((v,k) for k, v in urls_views.iteritems())
    base = urls_views_inverse[f]
    args = [base64.b64encode(a) for a in args if a]
    return thisPluginUrl+("/".join([base]+args))

@isUrl('list_ipods')
def firstLevel():
    "List the founs iPods and copy all the info"
    listipods = [m for m in sys_utils.get_mounts() if os.path.exists(os.path.join(m,'iPod_Control','iTunes','iTunesDB'))]
    for m in listipods:
        copyInfo(m)
        MyAddDirectoryItem(make_Url(ListAllAlbums,m),m,isFolder=True)
    xbmcplugin.endOfDirectory(thisPlugin)

#queries: albums

@isUrl('all_albums')
def ListAllAlbums(mp):
    d = shelve.open(ipodDB)
    albums = d[mp]
    ViewListAlbums(mp,sorted(albums))
    d.close()
        

def ViewListAlbums(mp,albumlist):
    for a in albumlist:
        if a:
            MyAddDirectoryItem(make_Url(ListAllSongsFromAlbum,mp,a),a,isFolder=True)
    xbmcplugin.endOfDirectory(thisPlugin)

#queries: songs

@isUrl('songs_from_album')
def ListAllSongsFromAlbum(mp,album):
    d = shelve.open(ipodDB)
    albums = d[mp]
    d.close()
    ViewListSongs(sorted(albums[album]['songs'],key=lambda s1: s1['track number']))


def ViewListSongs(songs):
    for s in songs:
        MyAddDirectoryItem(s['file'],s['title'])
    xbmcplugin.endOfDirectory(thisPlugin)

def main(a1,a2):
    global thisPlugin
    thisPlugin = int(a2)
    
    call_Url(a1)

if __name__ == "__main__":
    main(sys.argv[0],sys.argv[1])

