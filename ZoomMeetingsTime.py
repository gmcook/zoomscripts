# This script was created to get total meeting recordings for a Zoom account as well as estimated file size based on average recording quality
# by default, this asks you to define a date/time range from which to grab recordings
import http.client
from datetime import datetime as DT, datetime
import json
import os
import requests
import time
import jwt
def parse_time(s):
    hour, minute, sec = s.split(':')
    try:
        hour = int(hour)
        minute = int(minute)
        sec = int(sec)
    except ValueError:
        # handle errors here, but this isn't a bad default to ignore errors
        return 0
    return hour * 60 * 60 + minute * 60 + sec
#define a zoomapi token, this is from Zoom Admin page (use JWT for auth)
key = ''
secret = ''
# change start_time and end_time using datetime variables at top, this will depend on how often script runs
start_time_in = input('Please input start date: YYYY-MM-DD: ')
end_time_in = input('Please input end date: YYYY-MM-DD: ')
#start_time = DT.datetime.strptime(start_time_in, '%Y-%m-%d')
#end_time = DT.datetime.strptime(end_time_in, '%Y-%m-%d')
created = []
skipped = []
users = []
downloaded = []
cumulative = 0


skipped_count = 0
created_count = 0

header = {"alg": "HS256", "typ": "JWT"}
payload = {"iss": key, "exp": int(time.time() + 3600000)}
token = jwt.encode(payload, secret, algorithm="HS256", headers=header)
jwt_token=token.decode("utf-8")

conn2 = http.client.HTTPSConnection("api.zoom.us")
zoomheaders = {
    'authorization': "Bearer "+ jwt_token,
    'content-type': "application/json"
    }
q_string = "/v2/accounts/me/recordings?to=%s&from=%s&page_size=50&next_page_token=" % (end_time_in,start_time_in)
conn2.request("GET",q_string, headers=zoomheaders)

res = conn2.getresponse()
data = res.read()
recording_info = json.loads(data)

from_date = recording_info['from']
to_date = recording_info['to']
next_page = recording_info['next_page_token']
total_records_in = recording_info['total_records']
page_size_in = recording_info['page_size']
meeting_list = recording_info['meetings']
difference = 0
# get page count from total records and page_size requested
#if there are no pages returned exit
if page_size_in == 0:
    print("no videos found")
    exit()

page_count = int(total_records_in/page_size_in)
print(from_date)
print(to_date)
print(next_page)
print(total_records_in)
#print(meeting_list)
#print(page_count)

for i in range(1, page_count+1):  # start at page index 1 since we already have the first page
    q_string2 = "/v2/accounts/me/recordings?to=%s&from=%s&page_size=50&next_page_token=%s" % (end_time_in,start_time_in,next_page)
    #print(q_string2)
    conn2.request("GET", q_string2, headers=zoomheaders)
    res = conn2.getresponse()
    data = res.read()
    recording_info = json.loads(data)
    next_page = recording_info['next_page_token'] # update with new token
    meeting_list.extend(recording_info['meetings'])


print(len(meeting_list),"meetings of ",total_records_in, "total records returned")

recordings = []
usable_recordings = []
count_out = 0
file_size_load = 0
for m in meeting_list:
    topics = m['topic']
    customer_id = m['host_id']
    customer_email = m['host_email']
    # print(topics)

    # write out topic of the meetings before we dig into the recordings, change to DB statement
    # f.write(topics+ '\n')
    recordings = m['recording_files']
    print(m)
    # digs into the recordings fo meetings and writes the URL for each file(there may be multiple for each meeting topic)
    for r in recordings:
        templist0 = []
        templist1 = []
        timestamps = r['recording_start']
        endtimestamps=r['recording_end']



        # there are sometimes weird files that use File_type rather than recording_type, this fixes that issue
        try:
            filetype = r['recording_type']
            file_size_load = r['file_size'] + file_size_load
        except Exception as e:
            filetype = r['file_type']
            pass
        #print(filetype)
        if (filetype in ['shared_screen_with_speaker_view']):
            starttimestamp = r['recording_start']
            endtimestamp = r['recording_end']
            try:
                d1 = starttimestamp.replace('T', '').replace('Z', '')
                d2 = endtimestamp.replace('T', '').replace('Z', '')
                fd1: datetime = DT.strptime(d1, "%Y-%m-%d%H:%M:%S")
                fd2 = DT.strptime(d2, "%Y-%m-%d%H:%M:%S")
                difference = fd2-fd1
                str_difference = str(difference)
                fixed_difference = parse_time(str_difference)
                cumulative += fixed_difference
                print(fixed_difference)
                print(cumulative)
            except Exception as e:
                pass

        # fixing timestamps to be more readable and establishing temp variables
        timestamps_fixed = timestamps.replace('-', '_').replace(':', '')
        count_out += 1
file_size_load = file_size_load * .000000001
print('total file size: ', file_size_load, 'GB')

print(cumulative / 60 / 60)