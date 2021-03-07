import datetime
import requests
import re
import json


class Event:

    def __init__(self, events_desc: list):
        time = events_desc[2].lstrip("DTSTART;TZID=Europe/Paris:")
        self.beginTime: datetime.datetime = datetime.datetime(year=int(time[0:4]), month=int(time[4:6]),
                                                              day=int(time[6:8]),
                                                              hour=int(time[9:11]),
                                                              minute=int(time[11:13]), second=int(time[13:15]))
        time = events_desc[3].lstrip("DTEND;TZID=Europe/Paris:")
        self.endTime: datetime.datetime = datetime.datetime(year=int(time[0:4]), month=int(time[4:6]),
                                                            day=int(time[6:8]),
                                                            hour=int(time[9:11]),

                                                            minute=int(time[11:13]), second=int(time[13:15]))
        self.name = None
        self.teacher = None
        self.room = None
        for event in events_desc:
            if event.startswith("SUMMARY:"):
                self.name = event.lstrip("SUMMARY").lstrip(":")
            elif event.startswith("DESCRIPTION"):
                self.teacher = event.lstrip("DESCRIPTION:Profs").lstrip(" : ")
            elif event.startswith("LOCATION:"):
                self.room = event.lstrip("LOCATION:")

    def __str__(self):
        time = f"{self.beginTime.strftime('%Hh%M')}-{self.endTime.strftime('%Hh%M')}"
        teacher = f"\n{self.teacher}" if self.teacher is not None else ""
        room = f"\n({self.room})" if self.room is not None else ""
        return time + teacher + room


class Calendar:
    def UpdateCalendar(self):
        self.Calendar = list()
        r = requests.get(self.link)
        if not r.ok:
            raise Exception("Impossible to get .ics calendar")

        for event in re.findall(r"BEGIN:VEVENT\n((.|\n)*?)\nEND:VEVENT", r.text, re.MULTILINE):
            self.Calendar.append(Event(event[0].split('\n')))

        self.Calendar.sort(key=lambda x: x.beginTime)

    def __init__(self, link=None):
        self.Calendar = list()
        self.link = link
        if link is not None:
            self.UpdateCalendar()

    def __GetEventsOfDay(self, day: datetime.datetime):
        result = list()
        for event in self.Calendar:
            if event.beginTime.date() == day.date():
                result.append(event)
        return result

    def getClassOfTheDay(self):
        return self.__GetEventsOfDay(datetime.datetime.utcnow())

    def getClassOfTomorrow(self):
        return self.__GetEventsOfDay(datetime.datetime.utcnow() + datetime.timedelta(days=1))

    def getnplus(self, n: int):
        return self.__GetEventsOfDay(datetime.datetime.utcnow() + datetime.timedelta(days=n))


if __name__ == "__main__":
    calendar = Calendar("https://ichronos.net/feed/INFOS2E1-1.ics")
    # 340

    events = calendar.getnplus(2)
    events = calendar.getnplus(3)
    events = calendar.getnplus(4)
    print(1)
