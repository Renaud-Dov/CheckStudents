import language.en as lang

lang.getlang().toto


# #!/usr/bin/env python3
#
# import argparse
# import re
# import logging
#
# import requests
# import ics
#
#
# API = 'http://v3.webservices.chronos.epita.net/api/v3'
# RANGE = 3
# PRODID = '-//Laboratoire Assistant <acu@acu.epita.fr>//chronos.py//EN'
#
#
# def join_names(i):
#     return ', '.join([x.get('Name') for x in i])
#
#
# def chronos(promo, group):
#     logging.warning('{} {}'.format(group, promo))
#     r = requests.get('{}/Planning/GetRangeWeek/{}/{}'.format(API, group, RANGE))
#     if r.status_code != 200:
#         logging.error('cannot get API informations for {}'.format(group))
#         return
#
#     cal = ics.Calendar(creator=PRODID)
#     for week in r.json():
#         for day in week.get('DayList'):
#             for c in day.get('CourseList'):
#                 prof = join_names(c.get('StaffList'))
#                 room = join_names(c.get('RoomList'))
#                 groups = join_names(c.get('GroupList'))
#
#                 name = '{}'.format(c.get('Name'))
#                 name = re.sub(r"[^\w]", "_", name)
#                 uid = 'chronos-{}-{}-{}'.format(
#                     promo, c.get('BeginDate'), name)
#                 uid = uid.replace(' ', '_')
#
#                 summary = '{}'.format(c.get('Name'))
#                 if prof:
#                     summary += ' - {}'.format(prof)
#                 summary += ' ({})'.format(room)
#
#                 description = '\n'.join({
#                     "Cours: {}".format(c.get('Name')),
#                     "Prof: {}".format(prof),
#                     "Salle: {}".format(room),
#                     "Groupes: {}".format(groups),
#                 }).replace(',', '\\,')
#
#                 cal.events.append(ics.Event(
#                     name=summary,
#                     begin=c.get('BeginDate'),
#                     end=c.get('EndDate'),
#                     uid=uid,
#                     description=description,
#                     location=room.capitalize()
#                 ))
#
#     return cal
#
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-promo")
#     parser.add_argument("-group")
#     args = parser.parse_args()
#     cal = chronos(promo=args.promo, group=args.group)
#     print(str(cal))