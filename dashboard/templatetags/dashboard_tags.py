from datetime import datetime

from dateutil.tz import tz
from django import template

register = template.Library()


@register.filter('timestamp_to_time')
def timestamp_date(arg):
    if arg == '1531188713':
        print(datetime.fromtimestamp(int(arg)).astimezone(tz.gettz('America/Chicago')))
    return datetime.fromtimestamp(int(arg)).astimezone(tz.gettz('America/Chicago')).strftime('%b %d %y,  %H:%M')


@register.filter('format_second')
def convert_second_to_hour(sec):
    h = int(sec/3600)
    m = int((sec % 3600)/60)
    return str(h)+" hours "+ str(m) + " minutes"


@register.filter('get_total_ads')
def get_total_ads(queryset, batch_id):
    batch_info = queryset.filter(batch_id=batch_id)
    if len(batch_info) > 0:
        return batch_info[0].get('total_ads')
    else:
        return 0