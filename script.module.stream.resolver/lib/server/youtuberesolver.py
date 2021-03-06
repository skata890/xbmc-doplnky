# -*- coding: UTF-8 -*-
'''
   YouTube plugin for XBMC
    Copyright (C) 2010-2012 Tobias Ussing And Henrik Mosgaard Jensen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import urllib
import cgi
import simplejson as json


class YoutubePlayer(object):
    fmt_value = {
            5: "240p",
            18: "360p",
            22: "720p",
            26: "???",
            33: "???",
            34: "360p",
            35: "480p",
            37: "1080p",
            38: "720p",
            43: "360p",
            44: "480p",
            45: "720p",
            46: "520p",
            59: "480",
            78: "400",
            82: "360p",
            83: "240p",
            84: "720p",
            85: "520p",
            100: "360p",
            101: "480p",
            102: "720p",
            120: "hd720",
            121: "hd1080"
            }

    # YouTube Playback Feeds
    urls = {}
    urls['video_stream'] = "http://www.youtube.com/watch?v=%s&safeSearch=none"
    urls['embed_stream'] = "http://www.youtube.com/get_video_info?video_id=%s"
    urls['video_info'] = "http://gdata.youtube.com/feeds/api/videos/%s"

    def __init__(self):
        pass
    
    def extractFlashVars(self, data):
        flashvars = {}
        found = False

        for line in data.split("\n"):
            if line.strip().find(";ytplayer.config = ") > 0:
                found = True
                p1 = line.find(";ytplayer.config = ") + len(";ytplayer.config = ") - 1
                p2 = line.rfind(";")
                if p1 <= 0 or p2 <= 0:
                    continue
                data = line[p1 + 1:p2]
                break

        if found:
            data = json.loads(data)
            flashvars = data["args"]

        return flashvars

    def scrapeWebPageForVideoLinks(self, result, video):
        links = {}
        flashvars = self.extractFlashVars(result)
        if not flashvars.has_key(u"url_encoded_fmt_stream_map"):
            return links

        if flashvars.has_key(u"ttsurl"):
            video[u"ttsurl"] = flashvars[u"ttsurl"]
        if flashvars.has_key("title"):
            video["title"] = flashvars["title"]

        for url_desc in flashvars[u"url_encoded_fmt_stream_map"].split(u","):
            url_desc_map = cgi.parse_qs(url_desc)
            if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
                continue

            key = int(url_desc_map[u"itag"][0])
            url = u""
            if url_desc_map.has_key(u"url"):
                url = urllib.unquote(url_desc_map[u"url"][0])
            elif url_desc_map.has_key(u"conn") and url_desc_map.has_key(u"stream"):
                url = urllib.unquote(url_desc_map[u"conn"][0])
                if url.rfind("/") < len(url) -1:
                    url = url + "/"
                url = url + urllib.unquote(url_desc_map[u"stream"][0])
            elif url_desc_map.has_key(u"stream") and not url_desc_map.has_key(u"conn"):
                url = urllib.unquote(url_desc_map[u"stream"][0])

            if url_desc_map.has_key(u"sig"):
                url = url + u"&signature=" + url_desc_map[u"sig"][0]

            links[key] = url

        return links

    def extractVideoLinksFromYoutube(self, url, videoid,video):
        result = util.request(self.urls[u"video_stream"] % videoid)
        links = self.scrapeWebPageForVideoLinks(result, video)
        if len(links) == 0:
            util.error(u"Couldn't find video url- or stream-map.")
        return links
#/*
# *      Copyright (C) 2011 Libor Zoubek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import re,util,urllib
__name__ = 'youtube'


def supports(url):
    return not _regex(url) == None

def resolve(url):
    m = _regex(url)
    if not m == None:
        player = YoutubePlayer()
        video = {'title':'žádný název'}
        links = player.extractVideoLinksFromYoutube(url,m.group('id'),video)
        resolved = []
        for q in links:
            if q in player.fmt_value.keys():                
                quality = player.fmt_value[q]
                item = {}
                item['name'] = __name__
                item['url'] = links[q]
                item['quality'] = quality
                item['surl'] = url
                item['subs'] = ''
                item['title'] = video['title']
        resolved.append(item)
        return resolved

def _regex(url):
    return re.search('https?\://www\.youtube\.com/(watch\?v=|v/|embed/)(?P<id>.+?)(\?|$|&)',url,re.IGNORECASE | re.DOTALL)

