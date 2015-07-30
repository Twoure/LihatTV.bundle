# LihatTV.bundle
Fork of the official [LihaTV](http://lihattv.com/) [Plex Media Server](https://plex.tv) bundle for development.
***

## API Documentation

### Syntax

```
http://{domain}/api/?q={query}  >>  http://lihattv.com/api/?q=islogin
```
pick one domain you like:

* lihattv.us
* lihattv.tv
* lihattv.tk
* lihattv.cf
* lihattv.ga
* lihattv.gq
* lihattv.ml
* lihattv.com
* lihattv.co.in
* lihattv.co.id
* lihattv.co.uk
* 7dplxsxxh54rxp4n.onion

---

### Basic Query
```bash
islogin # Knowing login status.
# result:
$ltv_id="23";$ltv_email="you@email.com";$ltv_poin="13";$ltv_level="1";
```
```bash
stats # Get user statistics.
# result:
$ltv_submit=0;$ltv_poin=11;
```
```bash
login&e={email}&p={password} # Access log in or sign up function.
# result (new account):
$ltv_status="new";
# result (un-activated):
$ltv_status="confirm";
# result (error in email or password):
$ltv_status="error";
# result (has log in):
$ltv_status="loged";
# result (login account):
$ltv_status="26|username|email|***|11|1";
```
```bash
logout # Access log out function.
# no result
```
---

### Result Query

<table>
<thead>
<tr>
<th>Query</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td>html&{parameter}</td>
<td>Generate database list show in HTML with play link.</td>
</tr>
<tr>
<td>xml&{parameter}</td>
<td>Generate database list via standard XML format.</td>
</tr>
<tr>
<td>rss&{parameter}</td>
<td>Generate database list via RSS (Rich Site Summary) format.</td>
</tr>
<tr>
<td>m3u&{parameter}</td>
<td>Generate database list via Winamp playlist format.</td>
</tr>
<tr>
<td>pls&{parameter}</td>
<td>Generate database list via SHOUTcast playlist format.</td>
</tr>
<tr>
<td>asx | wax | wvx &{parameter}</td>
<td>Generate database list via Microsoft playlist format.</td>
</tr>
<tr>
<td>kpl&{parameter}</td>
<td>Generate database list via Kazaa or KM-Player playlist format.</td>
</tr>
<tr>
<td>dpl&{parameter}</td>
<td>Generate database list via Daum PotPlayer format.</td>
</tr>
<tr>
<td>qpl&{parameter}</td>
<td>Generate database list via QPPlaylist format.</td>
</tr>
<tr>
<td>wpl&{parameter}</td>
<td>Generate database list via Windows Media Player playlist format.</td>
</tr>
<tr>
<td>fs&{parameter}</td>
<td>Generate database list via FreeSmith Player playlist format.</td>
</tr>
<tr>
<td>aimp2 | aimp3 &{parameter}</td>
<td>Generate database list via AIMP2 or AIMP3 playlist format.</td>
</tr>
<tr>
<td>smil&{parameter}</td>
<td>Generate database list via W3C format.</td>
</tr>
<tr>
<td>xspf&{parameter}</td>
<td>Generate database list via Xiph.Org Foundation playlist format.</td>
</tr>
<tr>
<td>xbmc&{parameter}</td>
<td>Generate database list via standard Kodi/XBMC playlist addons.</td>
</tr>
</tbody>
</table>

___
#### Details of parameter:

```
limit={max result a page}

page={page number}

search={search query}

channel={radio,tv,movies}

format={audio,flash,hls,webm,torrent,xbmc,vlc,wmp}

genre={adult,movies,news,kids,sport,etc...}

country={turkey,uae,uk,usa,dubai,etc...}

year={1997,2015,etc...}

stream={url/streamer addresses}
```

parameter is optional, you can use or not. default limit is 40 list a page, for example:
```
http://lihattv.com/api/?q=xml&search=!tb

http://lihattv.com/api/?q=asx&stream=mms://

http://lihattv.com/api/?q=kpl&format=webm

http://lihattv.com/api/?q=m3u&genre=news&limit=200

http://lihattv.com/api/?q=html&channel=movies&format=webm&limit=500
```
