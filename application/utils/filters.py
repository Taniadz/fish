import flask_babel
def format_datetime(value, format='medium'):
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="dd.MM.y HH:mm"
    return flask_babel.format_datetime(value, format)


from jinja2 import Markup

class momentjs(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        return Markup("<script>\nmoment.locale('ru')\ndocument.write(moment(\"%s\").%s);\n</script>" % (self.timestamp.strftime("%Y-%m-%dT%H:%M:%S Z"), format))

    def format(self, fmt):
        return self.render("format(\"%s\")" % fmt)

    def calendar(self):
        return self.render("calendar()")




    def fromNow(self):
        return self.render("fromNow()")

import pytz
from pytz import timezone
import tzlocal
def uk_timezone(value, format="%H:%M %d.%m"):
    tz = pytz.timezone('Europe/Kiev') # timezone you want to convert to from UTC
    utc = pytz.timezone('UTC')
    value = utc.localize(value).astimezone(tz)

    return value.strftime(format)
