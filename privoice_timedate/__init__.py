from skills.pvx_base import PriVoice
from threading import Event
import os
import datetime

class TimeSkill(PriVoice):
    def __init__(self, bus=None, timeout=5):
        super().__init__(skill_id='time_skill', skill_category='system')

        self.voice = 'p270'

        self.register_intent('Q', 'what', 'time', self.handle_time_match)
        self.register_intent('Q', 'what', 'date', self.handle_date_match)
        self.register_intent('Q', 'what', 'today', self.handle_date_match)
        self.register_intent('Q', 'what', 'day', self.handle_day_match)


    def handle_date_match(self,msg):
        now = datetime.datetime.now()
        text = now.strftime("%A %B %d %Y")
        # use system default voice
        self.speak(text)

    def handle_time_match(self,msg):
        now = datetime.datetime.now()
        text = now.strftime("%I %M %p")
        # use my default voice
        self.speak(text, voice=self.voice)

    def handle_day_match(self,msg):
        now = datetime.datetime.now()
        text = now.strftime("%A")
        self.speak(text, voice=self.voice)

    def stop(self,msg):
        print("\n*** Do nothing timedate skill stop hit ***\n")


if __name__ == '__main__':
    ts = TimeSkill()
    Event().wait()  # Wait forever

