####################################################################################################
#                                                                                                  #
#                               LihatTV Plex Channel -- v0.01                                      #
#                                                                                                  #
####################################################################################################
# set global variables
TITLE = 'LihatTV'
PREFIX = '/video/lihattv'
COUNTRIES = []

# set background art and icon defaults
ICON = 'icon-default.png'
ART = 'art-default.jpg'  #need better art
VIDEO_THUMB = 'icon.genre.png'
PREFS_ICON = 'icon.tools.png'

####################################################################################################
def Start():
    HTTP.CacheTime = 0

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(VIDEO_THUMB)
    DirectoryObject.art = R(ART)

    VideoClipObject.art = R(ART)

    ValidatePrefs(start=True)

####################################################################################################
@handler(PREFIX, TITLE, ICON, ART)
def MainMenu():
    oc = ObjectContainer(title2=TITLE)

    oc.add(DirectoryObject(key=Callback(DirectoryList, page=1), title='All'))
    oc.add(DirectoryObject(key=Callback(CountryList), title='Countries'))
    oc.add(DirectoryObject(key=Callback(GenreList), title='Genres'))
    oc.add(DirectoryObject(key=Callback(Bookmarks), title='My Bookmarks'))
    oc.add(PrefsObject(title='Preferences', thumb=R(PREFS_ICON)))
    oc.add(InputDirectoryObject(
        key=Callback(Search), title='Search', summary='Search LihatTV', prompt='Search for...'))

    return oc

####################################################################################################
@route(PREFIX + '/validateprefs', start=bool)
def ValidatePrefs(start=False):
    if Prefs['format'] == 'mms':
        Dict['format'] = 'mms://'
    elif Prefs['format'] == 'rtmp':
        Dict['format'] = 'rtmp://'
    elif Prefs['format'] == 'm3u8':
        Dict['format'] = '.m3u8'

    # Test domain url
    if not Dict['domain']:
        Dict['domain'] = Prefs['domain']

    if not Prefs['domain'] == Dict['domain'] or start:
        Dict['domain'] = Prefs['domain']
        url = 'http://' + Prefs['domain'] + '/admin/list.php'
        try:
            test = HTTP.Request(url).content
            if test == 'Can\'t connecting...':
                Logger('*' * 80, force=True)
                Logger('* test failed', kind='Warn', force=True)
                Logger('*' * 80, force=True)
                Dict['domain_test'] = 'Fail'
            else:
                Dict['domain_test'] = 'Pass'
                Logger('*' * 80, force=True)
                Logger('* %s Domain Passed Test' %Prefs['domain'], force=True)
                Logger('*' * 80, force=True)
        except:
            Logger('*' * 80, force=True)
            Logger('* Test failed. %s domain offline.' %Prefs['domain'], kind='Warn', force=True)
            Logger('*' * 80, force=True)
            Dict['domain_test'] = 'Fail'

    Dict.Save()

####################################################################################################
def DomainTest():
    """Setup MessageContainer if Dict[\'domain_test\'] failed"""

    if Dict['domain_test'] == 'Fail':
        return (False, MessageContainer(
            'Error',
            'Domain %s offline. Please pick a different Domain.' %Prefs['domain']))
    else:
        return (True, None)

####################################################################################################
@route(PREFIX + '/bookmarks')
def Bookmarks():
    if not Dict['Bookmarks']:
        return MessageContainer('Bookmarks', 'No Bookmarks yet. Get out there and start adding some!!!')

    oc = ObjectContainer(title2='My Bookmarks')

    info_list = []
    for bm in Dict['Bookmarks'].keys():
        bookmark = Dict['Bookmarks'][bm]
        video_info = {
            'title': bookmark['title'],
            'summary': bookmark['summary'],
            'tagline': bookmark['summary'],
            'genres': bookmark['genre'],
            'countries': bookmark['country'],
            'thumb': bookmark['thumb'],
            'art': bookmark['art'],
            'id': bookmark['id'],
            'url': 'http://' + Prefs['domain'] + '/?play=' + bookmark['id']
            }
        info_list.append(video_info)

    for sorted_bm in sorted(info_list, key=lambda k: k['title']):
        if not Prefs['adult'] and 'adult' in (sorted_bm['genres'][0].lower() if sorted_bm['genres'] else ''):
            continue
        elif Prefs['adult']:
            pass

        oc.add(DirectoryObject(
            key=Callback(VideoOptionPage, video_info=sorted_bm),
            title=sorted_bm['title'], summary=sorted_bm['summary'], tagline=sorted_bm['tagline'],
            thumb=R(sorted_bm['thumb']) if sorted_bm['thumb'] else None,
            art=R(sorted_bm['art']) if sorted_bm['art'] else None
            ))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Bookmarks', 'No Bookmarks yet. Get out there and start adding some!!!')

####################################################################################################
@route(PREFIX + '/genrelist')
def GenreList():
    """Get Genres for relevant category and stream"""

    (test, message) = DomainTest()
    if not test:
        return message

    main_title = 'Genres'
    oc = ObjectContainer(title2=main_title)

    stream = Dict['format']
    limit = 10000
    q = '/api/?q=html&channel=TV&stream=%s&limit=%i&page=1' %(stream, limit)
    url = 'http://' + Prefs['domain'] + q

    html = HTML.ElementFromURL(url, encoding='utf8', errors='ignore')

    genres = []
    for node in html.xpath('//ol/li'):
        node_text = node.text_content().strip()
        r = Regex('^(.+).+\((.+)[:](.+?)\ .(.+?)\)').search(node_text).group(3).strip()
        if not r in genres:
            genres.append(r)

    for genre in sorted(genres):
        if not Prefs['adult'] and 'adult' in genre.lower():
            continue
        elif Prefs['adult']:
            pass

        oc.add(DirectoryObject(
            key=Callback(DirectoryList, genre=genre, page=1),
            title=genre, summary='%s TV List ' %genre
            ))

    return oc

####################################################################################################
@route(PREFIX + '/coutnrylist')
def CountryList():
    """Setup Country List, some countries will not have streams"""

    (test, message) = DomainTest()
    if not test:
        return message

    main_title = 'Countries'
    oc = ObjectContainer(title2=main_title)

    url = 'http://' + Prefs['domain'] + '/admin/list.php?c=country'

    html = HTML.ElementFromURL(url)
    for country in html.xpath('//option/text()'):
        name = country.title()
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, country=name, page=1),
            title=name, summary='%s Country List ' %name
            ))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Currently search is just for \"TV Channel\""""

    (test, message) = DomainTest()
    if not test:
        return message

    search = String.Quote(query, usePlus=True)

    q = '/api/?q=xml&channel=TV&stream=%s&search=%s&limit=1&page=1' %(Dict['format'], query)
    url = 'http://' + Prefs['domain'] + q
    page_info = HTTP.Request(url).content.splitlines()
    page_el = XML.ElementFromString(page_info[0] + page_info[-1])
    if not int(page_el.get('total')) == 0:
        return DirectoryList(page=1, query=query)
    else:
        return MessageContainer('Search Warning',
            'There are no search results for \"%s\". Try being less specific.' %query)

####################################################################################################
@route(PREFIX + '/directorylist', page=int)
def DirectoryList(page, genre='', country='', query=''):
    """
    Return Channels based on input
    Genre, Country and Search are sent here
    """

    (test, message) = DomainTest()
    if not test:
        return message

    stream = Dict['format']
    limit = 500

    if not genre:
        genre = ''

    if not country:
        country = ''

    if not query:
        query = ''

    q = (
        '/api/?q=xml&channel=TV&genre=%s&country=%s&stream=%s&search=%s&limit=%i&page=%i'
        %(genre, country, stream, query, limit, page)
        )
    Logger('* q = %s' %q)
    url = 'http://' + Prefs['domain'] + q

    page_info = HTTP.Request(url).content.splitlines()
    r_info = page_info[0] + page_info[-1]
    Logger('* r_info = %s' %r_info)
    page_el = XML.ElementFromString(r_info)
    total = int(page_el.get('total'))
    if total == 0 and not genre == '':
        return MessageContainer('Warning', 'No %s Streams for %s TV List' %(stream, genre))
    elif total == 0 and not country == '':
        return MessageContainer('Warning', 'No %s Streams for %s TV List' %(stream, country))

    total_pgs = int(total/limit) + 1
    Logger('* total pages = %i' %total_pgs)
    Logger('* current page = %i' %page)

    if page == 1 and total_pgs == 1:
        if query:
            main_title = 'Search: \"%s\"' %query
        elif genre or country:
            main_title = 'Genre | %s' %genre if genre else 'Country | %s' %country
        else:
            main_title = 'TV'
    elif 1 < total_pgs == page:
        if query:
            main_title = 'Search: \"%s\" | Last page' %query
        elif genre or country:
            main_title = ('Genre | %s' %genre if genre else 'Country | %s' %country) + ' | Last Page'
        else:
            main_title = 'Last Page'
    elif 1 < total_pgs > page:
        if query:
            main_title = 'Search: \"%s\" | Page %i of %i' %(query, page, total_pgs)
        elif genre or country:
            main_title = ('Genre | %s' %genre if genre else 'Country | %s' %country) + ' | Page %i of %i' %(page, total_pgs)
        else:
            main_title = 'Page %i of %i' %(page, total_pgs)

    oc = ObjectContainer(title2=main_title)

    # setup url to parse html page
    q2 = (
        '/api/?q=html&channel=TV&genre=%s&country=%s&stream=%s&search=%s&limit=%i&page=%i'
        %(genre, country, stream, query, limit, page)
        )
    url2 = 'http://' + Prefs['domain'] + q2

    xml = HTML.ElementFromURL(url2, encoding='utf8', errors='ignore')

    for node in xml.xpath('//ol/li'):
        title_text = node.text_content().strip()
        r = Regex('^(.+).+\((.+)[:](.+?)\ .(.+?)\)').search(title_text)
        ch_title = r.group(1).strip()
        ch_category = r.group(2).strip()
        ch_genre = r.group(3).strip()
        ch_country = r.group(4).strip()
        tagline = 'Category: %s | Genre: %s | Country: %s' %(ch_category, ch_genre, ch_country)
        ch_url = node.xpath('./a/@href')[0].strip()
        video_id = str(ch_url.split('=')[1])

        video_info = {
            'title': ch_title,
            'summary': tagline,
            'tagline': tagline,
            'genres': [ch_genre],
            'countries': [ch_country],
            'thumb': VIDEO_THUMB,
            'art': ART,
            'id': video_id,
            'url': ch_url
            }

        if not Prefs['adult'] and 'adult' in ch_genre.lower():
            continue
        elif Prefs['adult']:
            pass

        oc.add(DirectoryObject(
            key=Callback(VideoOptionPage, video_info=video_info),
            title=ch_title, summary=tagline, tagline=tagline, thumb=R(VIDEO_THUMB)))

    if page < total_pgs and len(oc) > 0:
        oc.add(NextPageObject(
            key=Callback(DirectoryList,
                page=int(page) + 1, genre=genre, country=country, query=query),
            title='Next Page>>'))

    if len(oc) > 0:
        return oc
    else:
        return MessageContainer('Warning', 'No Streams Found')

####################################################################################################
@route(PREFIX + '/videooptionpage', video_info=dict)
def VideoOptionPage(video_info):
    """VideoObject and Bookmark function"""

    (test, message) = DomainTest()
    if not test:
        return message

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

    if Dict['Bookmarks']:
        if video_info['id'] in Dict['Bookmarks']:
            oc.add(DirectoryObject(
                key=Callback(RemoveBookmark, video_info=video_info),
                title='Remove Bookmark',
                summary = 'Remove \"%s\" from your Bookmarks list.' %video_info['title']))
        else:
            oc.add(DirectoryObject(
                key=Callback(AddBookmark, video_info=video_info),
                title='Add Bookmark',
                summary = 'Add \"%s\" to your Bookmarks list.' %video_info['title']))
    else:
        oc.add(DirectoryObject(
            key=Callback(AddBookmark, video_info=video_info),
            title='Add Bookmark',
            summary = 'Add \"%s\" to your Bookmarks list.' %video_info['title']))

    return oc

####################################################################################################
@route(PREFIX + '/addbookmark', video_info=dict)
def AddBookmark(video_info):
    """Add Bookmark"""

    new_bookmark = {
        'title': video_info['title'], 'id': video_info['id'], 'genre': video_info['genres'],
        'country': video_info['countries'], 'summary': video_info['summary'],
        'thumb': video_info['thumb'], 'art': video_info['art']
        }

    if not Dict['Bookmarks']:
        Dict['Bookmarks'] = {video_info['id']: new_bookmark}
    else:
        Dict['Bookmarks'].update({video_info['id']: new_bookmark})

    Dict.Save()

    return MessageContainer('Bookmarks',
        '\"%s\" has been added to your bookmarks.' %video_info['title'])

####################################################################################################
@route(PREFIX + '/removebookmark', video_info=dict)
def RemoveBookmark(video_info):
    """
    Remove Bookmark from Bookmark Dictionary
    If Bookmark to remove is the last Bookmark in the Dictionary,
    then Remove the Bookmark Dictionary also
    """

    if Dict['Bookmarks']:
        if video_info['id'] in Dict['Bookmarks'].keys():
            del Dict['Bookmarks'][video_info['id']]
            Dict.Save()

        if len(Dict['Bookmarks'].keys()) == 0:
            del Dict['Bookmarks']
            Dict.Save()

        return MessageContainer('Remove Bookmark',
            '\"%s\" has been removed from your bookmarks.' %video_info['title'])
    else:
        return MessageContainer('Bookmark Error', 'ERROR: \"%s\" cannot be removed. The Bookmark Dictionary does not exist!')

####################################################################################################
@route(PREFIX + '/logger', force=bool)
def Logger(message, force=False, kind=None):
    """Setup logging options based on prefs, indirect because it has no return"""

    if force or Prefs['debug']:
        if kind == 'Debug' or kind == None:
            Log.Debug(message)
        elif kind == 'Info':
            Log.Info(message)
        elif kind == 'Warn':
            Log.Warn(message)
        elif kind == 'Error':
            Log.Error(message)
        elif kind == 'Critical':
            Log.Critical(message)
        else:
            pass
    return
