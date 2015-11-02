####################################################################################################
#                                                                                                  #
#                               LihatTV Plex Channel -- v0.01                                      #
#                                                                                                  #
####################################################################################################
# set global variables
TITLE = 'LihatTV'
PREFIX = '/video/lihattv'
BASE_URL = 'http://lihattv.com/'

# set background art and icon defaults
ICON = 'icon-default.png'
ART = 'art-default.jpg'  #need better art
VIDEO_THUMB = 'icon.genre.png'
PREFS_ICON = 'icon.tools.png'

####################################################################################################
def Start():
    HTTP.CacheTime = 0
    HTTP.Headers['User-Agent'] = 'PLEX 1.0'

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(VIDEO_THUMB)
    DirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

####################################################################################################
@handler(PREFIX, TITLE, ICON, ART)
def MainMenu():
    oc = ObjectContainer(title2=TITLE)

    oc.add(DirectoryObject(key=Callback(DirectoryList, category='Movie', page=1), title='Movie'))
    oc.add(DirectoryObject(key=Callback(DirectoryList, category='Radio', page=1), title='Radio'))
    oc.add(DirectoryObject(key=Callback(DirectoryList, category='TV', page=1), title='TV'))
    oc.add(PrefsObject(title='Preferences', thumb=R(PREFS_ICON)))

    return oc

####################################################################################################
@route(PREFIX + '/directorylist', page=int)
def DirectoryList(category, page):
    #stream = 'mms'  # or 'rtmp' or 'm3u8'
    stream = Prefs['format']
    limit = 10

    q = 'api/?q=xml&channel=%s&stream=%s&limit=%i&page=%i' %(category, stream, limit, page)
    url = BASE_URL + q

    page_info = HTTP.Request(url).content.splitlines()
    r_info = page_info[0] + page_info[-1]
    Log('r_info = %s' %r_info)
    page_el = XML.ElementFromString(r_info)
    total = int(page_el.get('total'))
    total_pgs = int(total/limit)

    main_title = '%s | Page %i of %i' %(category, page, total_pgs)

    oc = ObjectContainer(title2=main_title)

    # setup url to parse xspf page
    q2 = 'api/?q=xspf&channel=%s&stream=%s&limit=%i&page=%i' %(category, stream, limit, page)
    url2 = BASE_URL + q2

    """
    test = HTTP.Request(url2).content
    #Log(test)
    xml = XML.ElementFromString(test, encoding='utf8')
    Log(xml.xpath('//playlist/title/text()')[0])
    """

    #xml = XML.ElementFromURL(url2, encoding='utf8')
    xml = HTML.ElementFromURL(url2, encoding='utf8')
    """
    Log(xml)
    for child in xml:
        Log('%s = %s' %(child.tag, child.text))

    Log(xml.xpath('.')[0].tag[0].tag)
    """

    for node in xml.xpath('//track'):
        Log('--------------------------------')
        title_string = node.xpath('./title/text()')[0]
        Log(title_string)
        r = Regex('\[(.+?)\](.+?)\((.+?)(?:\ .)(.+?)\)').search(title_string)
        ch_category = r.group(1).strip()
        Log(ch_category)
        ch_title = r.group(2).strip()
        Log(ch_title)
        ch_genre = r.group(3).strip()
        Log(ch_genre)
        ch_country = r.group(4).strip()
        Log(ch_country)
        tagline = 'Category: %s | Genre: %s | Country: %s' %(ch_category, ch_genre, ch_country)
        ch_url = node.xpath('./location/text()')[0].strip()
        Log(ch_url)

        oc.add(
            VideoClipObject(
                title=ch_title,
                summary=tagline,
                tagline=tagline,
                genres=[ch_genre],
                countries=[ch_country],
                thumb=R(VIDEO_THUMB),
                art=R(ART),
                url=ch_url
                )
            )

    if page < total_pgs and len(oc) > 0:
        oc.add(NextPageObject(
            key=Callback(
                DirectoryList, category=category, page=int(page)),
            title='Next Page>>'))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Warning', 'No Streams in %s' %category)
"""
####################################################################################################
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

####################################################################################################
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

####################################################################################################
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

####################################################################################################
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

####################################################################################################
def GetThumb(thumb):
    if thumb and thumb.startswith('http'):
        return thumb
    elif thumb and thumb <> '':
        return R(thumb)
    else:
        return R('icon.play.png')

####################################################################################################
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
"""
