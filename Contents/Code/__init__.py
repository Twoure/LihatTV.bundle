####################################################################################################
#                                                                                                  #
#                               LihatTV Plex Channel -- v0.01                                      #
#                                                                                                  #
####################################################################################################
# import modules
import base64

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
    #HTTP.Headers['User-Agent'] = 'PLEX 1.0'

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(VIDEO_THUMB)
    DirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

####################################################################################################
@handler(PREFIX, TITLE, ICON, ART)
def MainMenu():
    oc = ObjectContainer(title2=TITLE)

    oc.add(DirectoryObject(key=Callback(DirectoryOpt, category='Movies'), title='Movies'))
    oc.add(DirectoryObject(key=Callback(DirectoryOpt, category='Radio'), title='Radio'))
    oc.add(DirectoryObject(key=Callback(DirectoryOpt, category='TV'), title='TV'))
    oc.add(PrefsObject(title='Preferences', thumb=R(PREFS_ICON)))

    return oc

####################################################################################################
@route(PREFIX + '/directoryopt')
def DirectoryOpt(category):
    oc = ObjectContainer(title2=category)

    oc.add(DirectoryObject(key=Callback(DirectoryList, category=category, page=1), title='All'))
    oc.add(DirectoryObject(key=Callback(CountryList, category=category), title='Countries'))
    oc.add(DirectoryObject(key=Callback(GenreList, category=category), title='Genres'))

    return oc

####################################################################################################
@route(PREFIX + '/genrelist')
def GenreList(category):
    main_title = '%s | Genres' %category

    oc = ObjectContainer(title2=main_title)

    html = HTML.ElementFromURL('http://lihattv.com/admin/list.php')

    for genre in html.xpath('//option/text()'):
        name = genre.title()
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, category=category, genre=name, page=1),
            title=name, summary='%s %s List ' %(name, category)
            ))

    return oc

####################################################################################################
@route(PREFIX + '/coutnrylist')
def CountryList(category):
    main_title = '%s | Countries' %category

    oc = ObjectContainer(title2=main_title)

    html = HTML.ElementFromURL('http://lihattv.com/admin/list.php?c=country')

    for country in html.xpath('//option/text()'):
        name = country.title()
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, category=category, country=name, page=1),
            title=name, summary='%s %s List ' %(name, category)
            ))

    return oc

####################################################################################################
@route(PREFIX + '/directorylist', page=int)
def DirectoryList(category, page, genre=None, country=None):
    #stream = 'mms'  # or 'rtmp' or 'm3u8'
    stream = Prefs['format']
    limit = 500
    if not genre:
        genre = ''

    if not country:
        country=''

    q = 'api/?q=xml&channel=%s&genre=%s&country=%s&stream=%s&limit=%i&page=%i' %(category, genre, country, stream, limit, page)
    url = BASE_URL + q

    page_info = HTTP.Request(url).content.splitlines()
    r_info = page_info[0] + page_info[-1]
    Log('r_info = %s' %r_info)
    page_el = XML.ElementFromString(r_info)
    total = int(page_el.get('total'))
    if total == 0 and not genre == '':
        return MessageContainer('Warning', 'No %s Streams for %s %s List' %(stream, genre, category))
    elif total == 0 and not country == '':
        return MessageContainer('Warning', 'No %s Streams for %s %s List' %(stream, country, category))

    total_pgs = int(total/limit)

    main_title = '%s | Page %i of %i' %(category, page, total_pgs)

    oc = ObjectContainer(title2=main_title)

    # setup url to parse xspf page
    q2 = 'api/?q=xspf&channel=%s&genre=%s&country=%s&stream=%s&limit=%i&page=%i' %(category, genre, country, stream, limit, page)
    url2 = BASE_URL + q2

    xml = HTML.ElementFromURL(url2, encoding='utf8', errors='ignore')

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

        video_info = {
            'title': ch_title,
            'summary': tagline,
            'tagline': tagline,
            'genres': [ch_genre],
            'countries': [ch_country],
            'thumb': VIDEO_THUMB,
            'art': ART,
            'url': ch_url
            }

        oc.add(DirectoryObject(
            key=Callback(VideoOptionPage, video_info=video_info),
            title=ch_title, summary=tagline, tagline=tagline, thumb=R(VIDEO_THUMB)))

    if page < total_pgs and len(oc) > 0:
        oc.add(NextPageObject(
            key=Callback(
                DirectoryList, category=category, page=int(page) + 1),
            title='Next Page>>'))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Warning', 'No Streams in %s' %category)

####################################################################################################
#plan to add bookmark function here
@route(PREFIX + '/videooptionpage', video_info=dict)
def VideoOptionPage(video_info):
    oc = ObjectContainer(title2=video_info['title'])

    oc.add(VideoClipObject(
        title=video_info['title'],
        summary=video_info['summary'],
        tagline=video_info['tagline'],
        genres=video_info['genres'],
        countries=video_info['countries'],
        thumb=R(video_info['thumb']),
        art=R(video_info['art']),
        url=video_info['url']
        ))

    return oc

