import os
working_dir = os.environ.get('WORKING_DIR', '')
if len(working_dir) > 0:
    os.chdir(working_dir)
import time
import datetime
import urllib
import db_handler
import run_scrappers
from slackclient import SlackClient

slack_client = SlackClient(os.environ.get('SLACK_TOKEN'))


def get_noti_channel(channel_name):
    channels = slack_client.api_call('channels.list')
    if channels['ok']:
        return next(e['id'] for e in channels['channels'] if e['name'] == channel_name)
    return None


def send_slack_noti(message):
    channel_id = get_noti_channel('noti')
    if not channel_id:
        return

    slack_client.api_call('chat.postMessage', channel=channel_id,
                          text='\n'+message, username='lifemark',
                          icon_emoji=':robot_face:')


print('>>>>>>>>> time by ironcpa >>>>>>>>>>')
print(time.ctime())

t = datetime.datetime.now()
is_daily = int(str(t)[11:13]) == 0

dued_lifemarks = None
if is_daily:
    dued_lifemarks = db_handler.get_dued_lifemarks()
else:
    dued_lifemarks = db_handler.get_hourly_dued_lifemarks()

message = ''
if dued_lifemarks:
    print('dued items : ', len(dued_lifemarks))
    print(dued_lifemarks)

    for lm in dued_lifemarks:
        message += '{}:{}({}) is dued!\r\n'.format(lm[0],
                                                   lm[1],
                                                   lm[3])

    # if is_daily:
    params = {'target_fields': 'key',
              'keyword': ' '.join([str(lm[0]) for lm in dued_lifemarks])}
    link = 'lifemarks?{}'.format(urllib.parse.urlencode(params, quote_via=urllib.parse.quote))
    db_handler.add_lifemark(title='items due tommorow',
                            category='noti',
                            link=link,
                            desc=message)

    print('message sent', message)

    send_slack_noti(message)

# todo: run scrappers
run_scrappers.main()
