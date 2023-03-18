from skills.pvx_media_skill_base import MediaSkill
from threading import Event
import requests, time, json, glob, os
from framework.message_types import MSG_MEDIA

media_verbs = ['play', 'watch', 'listen']
def sort_on_vpc(k):
    return k['votes_plus_clicks']

class RadioSkill(MediaSkill):
    # Free radio serice that provides basic search capabilities.
    def __init__(self, bus=None, timeout=5):
        self.skill_id = 'radio_skill'
        super().__init__(skill_id=self.skill_id, skill_category='media')
        self.url = ''
        self.blacklist = [
                "icecast",
                ]
        self.log.debug("** Radio skill initialized, skill base dir is %s" % (self.skill_base_dir,))

    def domain_is_unique(self, stream_uri, stations):
        return True

    def _search(self, srch_term, limit):
        uri = "https://nl1.api.radio-browser.info/json/stations/search?hidebroken=true&limit=%s&name=" % (limit,)
        query = srch_term.replace(" ", "+")
        uri += query
        res = requests.get(uri)
        if res:
            return res.json()

        return []

    def blacklisted(self, stream_uri):
        for bl in self.blacklist:
            if bl in stream_uri:
                return True
        return False

    def search(self, srch_term, limit):
        unique_stations = {}
        stations = self._search(srch_term, limit)

        # whack dupes, favor .aac streams
        for station in stations:
            station_name = station.get('name'.replace("\n"," "), "")
            stream_uri = station.get('url_resolved','')
            if stream_uri != '' and not self.blacklisted(stream_uri):
                if station_name in unique_stations:
                    if not unique_stations[station_name]['url_resolved'].endswith('.aac'):
                        unique_stations[station_name] = station
                else:
                    if self.domain_is_unique(stream_uri, stations):
                        unique_stations[station_name] = station

        res = []
        for station in unique_stations:
            votes_plus_clicks = 0
            votes_plus_clicks += int( unique_stations[station].get('votes', 0) )
            votes_plus_clicks += int( unique_stations[station].get('clickcount', 0) )
            unique_stations[station]['votes_plus_clicks'] = votes_plus_clicks

            res.append( unique_stations[station] )

        res.sort(key=sort_on_vpc, reverse=True)

        return res

    def play(self, uri):
        self.play_media(uri, False, 'stream_vlc')

    def get_media_confidence(self,msg):
        # I am being asked if I can handle this request
        sentence = msg.data['msg_sentence']
        self.log.debug("radio_skill handle query sentence=%s" % (sentence,))
        sa = sentence.split(" ")
        vrb = sa[0].lower()
        if vrb in media_verbs:
            sentence = sentence[len(vrb):]

        search_terms = sentence.replace(" ", "+")  # url encode it :-)
        limit = 1000
        stations = self.search(search_terms, limit)
        if len(stations) > 0:
            self.log.info("Radio - got some stations")
            station_name = stations[0].get('name'.replace("\n"," "), "")
            self.log.info("Playing %s" % (station_name,))
            self.url = stations[0].get('url_resolved','')
            self.log.info("Radio - URI is %s" % (self.url,))

        confidence = 0
        if self.url != '':
            confidence = 100

        return {'confidence':confidence, 'correlator':0, 'sentence':sentence, 'url':self.url}

    def media_play(self,msg):
        # I am being asked to play this media
        data = msg.data['skill_data']
        self.log.debug("\nRadio media play = %s" % (data,))
        sentence = data.get('sentence','')
        stream_uri = data.get('url','')
        self.log.error("\n** Radio playing %s from %s" % (sentence, stream_uri))
        #self.play_media(stream_uri, False, 'stream_vlc')
        self.play_media(stream_uri, False, 'mp3')

    def stop(self, msg):
        # TODO use media msg to cancel
        self.log.debug("Radio stop() hit. killall vlc")
        cmd = "killall cvlc"
        os.system(cmd)
        cmd = "killall mpg123"
        os.system(cmd)

if __name__ == '__main__':
    rs = RadioSkill()
    Event().wait()  
