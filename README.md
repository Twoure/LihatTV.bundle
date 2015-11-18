LihatTV.bundle
==============

Fork of the official [LihatTV](http://lihattv.com/) Plex bundle.
Developing this Channel for better implementation in [Plex Media Server](https://plex.tv).
This is a plugin that creates a new channel in [Plex Media Server](https://plex.tv) to view content from [LihatTV](http://lihattv.com/). It is currently under development and as such, should be considered alpha software and potentially unstable.

**Note:** the author of this plugin has no affiliation with [LihatTV](http://lihattv.com/) nor the owners of the content that they host.

Features
--------

- Watch Live IPTV & Radio streams
- Select streams (m3u8, mms, or rtmp)
- Search
- Bookmarks

Channel Support
---------------

#####**Plex Media Server:**
- Streams
  - mms:  Requires Silverlight
  - rtmp: Not Sure on requirements
  - m3u8: No requirements
- Tested Working:
  - Ubuntu 14.04 LTS: PMS version 0.9.12.19
  - Windows 7 & 10: PMS version 0.9.12.13

#####**Plex Clients:**
- Tested Working:
  - Plex Home Theater (Ubuntu 14.04 LTS, and Windows 7 & 10) (m3u8)
  - Android (4.4.2) (m3u8)
  - Plex/Web (2.4.23) (m3u8, rtmp)
- Not Working:
  - Chromecast (m3u8, rtmp, mms)
  - Android (4.4.2) (rtmp, mms)

How To Install
--------------

- [Download](https://github.com/Twoure/LihatTV.bundle/archive/master.zip) and install it by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
- Unzip and rename the folder to "LihatTV.bundle"
- Copy LihatTV.bundle into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
- ~~Restart PMS~~ **This is old, should not have to restart PMS.  If channel does not appear then Restart PMS**

Known Issues
------------
- Channel = Movies, mp4 streams are old style google picasa links with set timeout.  Most links have expired
- Stream = mms, requires silverlight.  May work on Windows OS, but need to test first
- Stream = rtmp, shows up on Plex Web client but not Android

ChangeLog
---------

**0.00** - 11/01/15 - Uploaded Fork of LihatTV.bundle from LihatTV site.  Added API documentation, refer to "ref" branch for original.
