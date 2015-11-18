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
COUNTRIES = []

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

    #oc.add(DirectoryObject(key=Callback(DirectoryOpt, category='Movies'), title='Movies'))
    oc.add(DirectoryObject(key=Callback(DirectoryOpt, category='TV'), title='TV'))
    oc.add(DirectoryObject(key=Callback(DirectoryOpt, category='Radio'), title='Radio'))
    oc.add(PrefsObject(title='Preferences', thumb=R(PREFS_ICON)))
    oc.add(InputDirectoryObject(
        key=Callback(Search), title='Search', summary='Search LihatTV', prompt='Search for...'))

    return oc

####################################################################################################
@route(PREFIX + '/validateprefs')
def ValidatePrefs():
    if Prefs['format'] == 'mms':
        Dict['format'] = 'mms://'
    elif Prefs['format'] == 'rtmp':
        Dict['format'] = 'rtmp://'
    elif Prefs['format'] == 'm3u8':
        Dict['format'] = '.m3u8'

    # Test domain url
    url = 'http://' + Prefs['domain'] + '/admin/list.php'
    try:
        test = HTTP.Request(url).content
        if test == 'Can\'t connecting...':
            Log('test failed')
            Dict['domain_test'] = 'Fail'
        else:
            Dict['domain_test'] = 'Pass'
            Log('%s Domain Passed Test' %Prefs['domain'])
    except:
        Log('Test failed. %s domain offline.' %Prefs['domain'])
        Dict['domain_test'] = 'Fail'

    Dict.Save()

####################################################################################################
@route(PREFIX + '/messagepopup')
def MessagePopUP():
    return MessageContainer(
        'Error',
        'Domain %s offline. Please pick a different Domain.' %Prefs['domain'])

####################################################################################################
@route(PREFIX + '/directoryopt')
def DirectoryOpt(category):
    if Dict['domain_test'] == 'Fail':
        return MessageContainer(
            'Error',
            'Domain %s offline. Please pick a different Domain.' %Prefs['domain'])

    oc = ObjectContainer(title2=category)

    oc.add(DirectoryObject(key=Callback(DirectoryList, category=category, page=1), title='All'))
    oc.add(DirectoryObject(key=Callback(CountryList, category=category), title='Countries'))
    oc.add(DirectoryObject(key=Callback(GenreList, category=category), title='Genres'))

    return oc

####################################################################################################
@route(PREFIX + '/genrelist')
def GenreList(category):
    if Dict['domain_test'] == 'Fail':
        return MessageContainer(
            'Error',
            'Domain %s offline. Please pick a different Domain.' %Prefs['domain'])

    main_title = '%s | Genres' %category

    oc = ObjectContainer(title2=main_title)

    stream = Dict['format']
    #stream = Prefs['format']
    limit = 10000

    q = '/api/?q=html&channel=%s&stream=%s&limit=%i&page=1' %(category,  stream, limit)
    url = 'http://' + Prefs['domain'] + q

    html = HTML.ElementFromURL(url, encoding='utf8', errors='ignore')

    genres = []
    for node in html.xpath('//ol/li'):
        node_text = node.text_content().strip()
        r = Regex('^(.+).+\((.+)[:](.+?)\ .(.+?)\)').search(node_text).group(3).strip()
        if not r in genres:
            genres.append(r)

    for genre in sorted(genres):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, category=category, genre=genre, page=1),
            title=genre, summary='%s %s List ' %(genre, category)
            ))

    #Log('Genres = %s' %genres)

    """
    html = HTML.ElementFromURL('http://lihattv.com/admin/list.php')
    #html = HTML.ElementFromURL('http://lihattv.com/admin/list.php?c=genre')

    for genre in html.xpath('//option/text()'):
        name = genre.title()
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, category=category, genre=name, page=1),
            title=name, summary='%s %s List ' %(name, category)
            ))
    """

    return oc

####################################################################################################
@route(PREFIX + '/coutnrylist')
def CountryList(category):
    if Dict['domain_test'] == 'Fail':
        return MessageContainer(
            'Error',
            'Domain %s offline. Please pick a different Domain.' %Prefs['domain'])

    main_title = '%s | Countries' %category

    oc = ObjectContainer(title2=main_title)

    """
    stream = Prefs['format']
    limit = 1

    q = '/api/?q=html&channel=%s&stream=%s&limit=%i&page=1' %(category,  stream, limit)
    url = 'http://' + Prefs['domain'] + q

    html = HTML.ElementFromURL(url, encoding='utf8', errors='ignore')

    countries = []
    for node in html.xpath('//ol/li'):
        node_text = node.text_content().strip()
        r = Regex('^(.+).+\((.+)[:](.+?)\ .(.+?)\)').search(node_text).group(4).strip()
        if not r in countries:
            countries.append(r)

    for country in sorted(countries):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, category=category, country=country, page=1),
            title=country, summary='%s %s List ' %(country, category)
            ))
    """
    url = 'http://' + Prefs['domain'] + '/admin/list.php?c=country'

    html = HTML.ElementFromURL(url)
    for country in sorted(html.xpath('//option/text()')):
        name = country.title()
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, category=category, country=name, page=1),
            title=name, summary='%s %s List ' %(name, category)
            ))
    """
    qevent = Thread.Event()
    qevent.clear()

    countries = []
    for country in html.xpath('//option/text()'):
        countries.append(country.title())

    total = len(countries)

    for i, c in enumerate(countries):
        if i < total:
            timer = float(Util.RandomInt(0,i)) + Util.Random()
            Thread.CreateTimer(timer, country_list, category=category, country=c)
        else:
            Thread.CreateTimer(timer, country_list, category=category, country=c, qevent=qevent)

    qevent.wait()

    for fc in COUNTRIES:
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, category=category, country=fc, page=1),
            title=fc, summary='%s %s List ' %(fc, category)
            ))
    """
    """
        name = fc.title()
        q = '/api/?q=xml&channel=%s&stream=%s&country=%s&limit=1&page=1' %(category, Dict['format'], name)
        c_url = 'http://' + Prefs['domain'] + q
        page_info = HTTP.Request(c_url).content.splitlines()
        page_el = XML.ElementFromString(page_info[0] + page_info[-1])

        if not int(page_el.get('total')) == 0:
            oc.add(DirectoryObject(
                key=Callback(DirectoryList, category=category, country=name, page=1),
                title=name, summary='%s %s List ' %(name, category)
                ))
    """

    return oc

####################################################################################################
def country_list(category, country, qevent=None):
    q = '/api/?q=xml&channel=%s&stream=%s&country=%s&limit=1&page=1' %(category, Dict['format'], country)
    url = 'http://' + Prefs['domain'] + q
    page_info = HTTP.Request(url).content.splitlines()
    page_el = XML.ElementFromString(page_info[0] + page_info[-1])
    if not qevent:
        if not int(page_el.get('total')) == 0:
            COUNTRIES.append(country)
        Log('Current Country Count = %i' %len(COUNTRIES))
        Log('Current Country List = %s' %COUNTRIES)
    elif qevent:
        if not int(page_el.get('total')) == 0:
            COUNTRIES.append(country)
        Log('Final Country Count = %i' %len(COUNTRIES))
        Log('Final Country List = %s' %COUNTRIES)
        qevent.set()

    return

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Currently search is just for \"TV Channel\""""

    if Dict['domain_test'] == 'Fail':
        return MessageContainer(
            'Error',
            'Domain %s offline. Please pick a different Domain.' %Prefs['domain'])

    search = String.Quote(query, usePlus=True)

    q = '/api/?q=xml&channel=TV&stream=%s&search=%s&limit=1&page=1' %(Dict['format'], query)
    url = 'http://' + Prefs['domain'] + q
    page_info = HTTP.Request(url).content.splitlines()
    page_el = XML.ElementFromString(page_info[0] + page_info[-1])
    if not int(page_el.get('total')) == 0:
        return DirectoryList(category='TV', page=1, query=query)
    else:
        return MessageContainer('Search Warning',
            'There are no search results for \"%s\". Try being less specific.' %query)

####################################################################################################
@route(PREFIX + '/directorylist', page=int)
def DirectoryList(category, page, genre='', country='', query=''):
    if Dict['domain_test'] == 'Fail':
        return MessageContainer(
            'Error',
            'Domain %s offline. Please pick a different Domain.' %Prefs['domain'])

    #stream = 'mms'  # or 'rtmp' or 'm3u8'
    #stream = Prefs['format']
    stream = Dict['format']
    limit = 500

    if not genre:
        genre = ''

    if not country:
        country = ''

    if not query:
        query = ''

    q = '/api/?q=xml&channel=%s&genre=%s&country=%s&stream=%s&search=%s&limit=%i&page=%i' %(category, genre, country, stream, query, limit, page)
    Log('q = %s' %q)
    url = 'http://' + Prefs['domain'] + q

    page_info = HTTP.Request(url).content.splitlines()
    r_info = page_info[0] + page_info[-1]
    Log('r_info = %s' %r_info)
    page_el = XML.ElementFromString(r_info)
    total = int(page_el.get('total'))
    if total == 0 and not genre == '':
        return MessageContainer('Warning', 'No %s Streams for %s %s List' %(stream, genre, category))
    elif total == 0 and not country == '':
        return MessageContainer('Warning', 'No %s Streams for %s %s List' %(stream, country, category))

    total_pgs = int(total/limit) + 1
    Log('total pages = %i' %total_pgs)
    Log('current page = %i' %page)

    if page == 1 and total_pgs == 1:
        if query:
            main_title = '%s | Search: \"%s\"' %(category, query)
        elif genre or country:
            main_title = '%s | %s' %(category, genre if genre else country)
        else:
            main_title = category
    elif 1 < total_pgs == page:
        if query:
            main_title = '%s | Search: \"%s\" | Last page' %(category, query)
        elif genre or country:
            main_title = '%s | %s | Last Page' %(category, genre if genre else country)
        else:
            main_title = '%s | Last Page' %category
    elif 1 < total_pgs > page:
        if query:
            main_title = '%s | Search: \"%s\" | Page %i of %i' %(category, query, page, total_pgs)
        elif genre or country:
            main_title = '%s | %s | Page %i of %i' %(category, genre if genre else country, page, total_pgs)
        else:
            main_title = '%s | Page %i of %i' %(category, page, total_pgs)

    oc = ObjectContainer(title2=main_title)

    # setup url to parse xspf page
    q2 = '/api/?q=html&channel=%s&genre=%s&country=%s&stream=%s&search=%s&limit=%i&page=%i' %(category, genre, country, stream, query, limit, page)
    #q2 = '/api/?q=xspf&channel=%s&genre=%s&country=%s&stream=%s&limit=%i&page=%i' %(category, genre, country, stream, limit, page)
    url2 = 'http://' + Prefs['domain'] + q2

    xml = HTML.ElementFromURL(url2, encoding='utf8', errors='ignore')

    #for node in xml.xpath('//track'):
    for node in xml.xpath('//ol/li'):
        #Log('--------------------------------')
        title_text = node.text_content().strip()
        r = Regex('^(.+).+\((.+)[:](.+?)\ .(.+?)\)').search(title_text)
        #title_string = node.xpath('./title/text()')[0]
        #Log(title_text)
        #r = Regex('\[(.+?)\](.+?)\((.+?)(?:\ .)(.+?)\)').search(title_string)
        ch_category = r.group(2).strip()
        #Log(ch_category)
        ch_title = r.group(1).strip()
        #Log(ch_title)
        ch_genre = r.group(3).strip()
        #Log(ch_genre)
        ch_country = r.group(4).strip()
        #Log(ch_country)
        tagline = 'Category: %s | Genre: %s | Country: %s' %(ch_category, ch_genre, ch_country)
        #ch_url = node.xpath('./location/text()')[0].strip()
        ch_url = node.xpath('./a/@href')[0].strip()
        #Log(ch_url)

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
            key=Callback(DirectoryList,
                category=category, page=int(page) + 1, genre=genre, country=country, query=query),
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

