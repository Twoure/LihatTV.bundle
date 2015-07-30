# Copyright © July, 05 2014 lihattv

TITLE = 'lihattv | Live TV Streaming'
PREFIX = '/video/lihattv'
ICON = R('icon-default.png')
ART = R('icon.art.png')
FOLDER = R('icon.genre.png')
TOOLS = R('icon.tools.png')
DOMAIN = 'http://lihattv.com/'

def Start():
    HTTP.CacheTime = 0
    ObjectContainer.title1 = TITLE
    DirectoryObject.thumb = FOLDER
    ObjectContainer.art = ART
    DirectoryObject.art = ART
    VideoClipObject.art = ART

@handler(PREFIX, TITLE)
def MainMenu():
    empty_group = False
    groups_list = []
    items_dict = {}
    HTTP.Headers['User-agent'] = 'PLEX 1.0'
    playlist = HTTP.Request(DOMAIN).content
    if playlist <> None:
        lines = playlist.splitlines()
        count = 0
        for i in range(len(lines) - 1):
            line = lines[i].strip()
            if line.startswith('#EXTINF'):
                url = lines[i + 1].strip()
                title = line[line.rfind(',') + 1:len(line)].strip()
                thumb = GetAttribute(line, 'img')
                group = GetAttribute(line, 'group')
                if group == '':
                    empty_group = True
                    group = 'No Category'
                elif not group in groups_list:
                    groups_list.append(group)
                count = count + 1
                items_dict[count] = {'url': url, 'title': title, 'thumb': thumb, 'group': group, 'order': count}
                i = i + 1
        groups_list.sort(key = lambda s: s.lower())
        if empty_group:
            groups_list.append('No Category')

    oc = ObjectContainer()
    for group in groups_list:
        oc.add(DirectoryObject(
            key = Callback(ListItems, items_dict = items_dict, group = group),
            title = group
        ))
    oc.add(PrefsObject(title = 'Configuration', thumb = TOOLS))
    return oc

#@route(PREFIX + '/listitems', items_dict = dict)
def ListItems(items_dict, group):
    oc = ObjectContainer(title1 = L(group))
    items_list = []
    for i in items_dict:
        if items_dict[i]['group'] == group:
            items_list.append(items_dict[i])
    items_list.sort(key = lambda dict: dict['title'].lower())
    for item in items_list:
        oc.add(CreateVideoClipObject(
            url = item['url'],
            title = item['title'],
            thumb = item['thumb']
        ))
    return oc

#@route(PREFIX + '/createvideoclipobject')
def CreateVideoClipObject(url, title, thumb, container = False):
    vco = VideoClipObject(
        key = Callback(CreateVideoClipObject, url = url, title = title, thumb = thumb, container = True),
        #rating_key = url,
        url = url,
        title = title,
        thumb = GetThumb(thumb),
        items = [
            MediaObject(
                container = Container.MP4,
                video_codec = VideoCodec.H264,
                audio_codec = AudioCodec.AAC,
                audio_channels = 6,
                parts = [
                    PartObject(
                        key = GetVideoURL(url = url)
                    )
                ],
                optimized_for_streaming = True
            )
        ]
    )

    if container:
        return ObjectContainer(objects = [vco])
    else:
        return vco
    return vco

def GetVideoURL(url, live = True):
    if url.startswith('rtmp') and Prefs['rtmp']:
        if url.find(' ') > -1:
            stream = GetAttribute(url, 'stream', '=', ' ')
            playpath = GetAttribute(url, 'playpath', '=', ' ')
            app = GetAttribute(url, 'app', '=', ' ')
            swfurl = GetAttribute(url, 'swfurl', '=', ' ')
            pageurl = GetAttribute(url, 'pageurl', '=', ' ')
            url = url[0:url.find(' ')]
            return RTMPVideoURL(url=url, clip=playpath, swf_url=swfurl, live = live)
        else:
            return RTMPVideoURL(url = url, live = live)
    elif url.startswith('mms'):
        return WindowsMediaVideoURL(url = url)
    else:
        return HTTPLiveStreamURL(url = url)

def GetThumb(thumb):
    if thumb and thumb.startswith('http'):
        return thumb
    elif thumb and thumb <> '':
        return R(thumb)
    else:
        return R('icon.play.png')

def GetAttribute(text, a, y1 = '="', y2 = '"'):
    x = text.find(a)
    if x > -1:
        y = text.find(y1, x + len(a)) + len(y1)
        z = text.find(y2, y)
        if z == -1:
            z = len(text)
        return unicode(text[y:z].strip())
    else:
        return ''