#Python script to add users to specified groups in Zoom



import requests
import time
import jwt
import csv
import logging
from logging.config import dictConfig
# using datetime module
import datetime
# ct stores current time
ct = datetime.datetime.now()
print("current time:-", ct)

# set the output level for the Console (DEBUG, INFO, ERROR, etc))
consoleLevel = 'INFO'
# set the filename for the two file stream logs and max logfile rotation count (0 = no rotation)
mainLogFileName = 'main.log'
mainLogFileCount = 0
errorLogFileName = 'error.log'
errorLogFileCount = 0
# configure the logging, options for e-mail of results
LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['debug_console_handler'
                , 'info_rotating_file_handler'
                , 'error_file_handler'
                , 'critical_mail_handler'],
        },
        'my.main': {
            'level': 'WARNING',
            'propagate': False,
            'handlers': ['info_rotating_file_handler'],
        },
        'my.error': {
            'level': 'ERROR',
            'propagate': False,
            'handlers': ['error_file_handler'],
        },
    },
    'handlers': {
        'debug_console_handler': {
            'level': '' + consoleLevel + '',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'info_rotating_file_handler': {
            'level': 'DEBUG',
            'formatter': 'info',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs\\' + mainLogFileName + '',
            'encoding': 'utf8',
            'mode': 'w',
            'maxBytes': 1048576,
            'backupCount': mainLogFileCount
        },
        'error_file_handler': {
            'level': 'ERROR',
            'formatter': 'error',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs\\' + errorLogFileName + '',
            'encoding': 'utf8',
            'mode': 'w',
            'maxBytes': 1048576,
            'backupCount': errorLogFileCount
        },
        'critical_mail_handler': {
            'level': 'CRITICAL',
            'formatter': 'error',
            'class': 'logging.handlers.SMTPHandler',
            'mailhost': 'example@website.com',
            'fromaddr': 'example@website.com',
            'toaddrs': ['example@website.com', 'example@website.com'],
            'subject': 'Critical error with updateAnalytics script'
        }
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s'
        },
        'error': {
            'format': '%(asctime)s-%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s'
        },
    },

}

class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result) # or format into one line however you want to

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '') + '|'
        return s



# initialize the logging
logging.config.dictConfig(LOGGING_CONFIG)
# format log exceptions to single line for file based logs
f = OneLineExceptionFormatter('%(asctime)s-%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s ')
# Rolling over file log (each start on new log), logging config determines backup counts
for h in logging.getLogger('my.error').handlers:
    h.setFormatter(f)
for h in logging.getLogger('my.main').handlers:
    h.setFormatter(f)
logging.info("script started.")

# Define ZoomAPI key/secret
key = 'XXXX'
secret = 'XXXX'


header = {"alg": "HS256", "typ": "JWT"}
payload = {"iss": key, "exp": int(time.time() + 3600000)}
token = jwt.encode(payload, secret, algorithm="HS256", headers=header)
# remove this line if you get an error in the headers, this is version dependent
jwt_token = token.decode("utf-8")
headers = {
    'authorization': "Bearer " + jwt_token,
    'content-type': "application/json"
}

# csv file of users & group IDs format group, member
csvFileName = 'UserFile.csv'
# create a custom dialect for reading this csv file that ignores\removes leading spaces in field values
csv.register_dialect('zoomGroupDialect', quotechar='"', skipinitialspace=True, quoting=csv.QUOTE_NONE,
                     lineterminator='\n', strict=True)
# open the file for reading
with open(csvFileName, "r", newline='',encoding="UTF-8") as csvfile:
    # read the header line and strip any leading or trailing spaces from the fields to be used as dict keys
    header = [h.strip() for h in csvfile.readline().split(',')]
    # pull in the csv data as dict with header and dialect options
    reader = csv.DictReader(csvfile, fieldnames=header, dialect='zoomGroupDialect')
    # for each row in the file
    for row in reader:
        # log the group and user info for this row
        logging.info("group: " + row['group'] + ", user: " + row['member'])
        # create the URL using the group info
        url_address = "https://api.zoom.us/v2/groups/" + row['group'].strip() + "/members"

        # create the json for the member info, strip any leading or trailing spaces from the data
        groupMem = {
            "members": [
                {
                    "email": row['member'].strip()
                }
                ]
                }
        # send Post request with URL, headers and json
        r = requests.post(url=url_address, headers=headers, json=groupMem).json()
        print(r)
        # output the info for the added members
        logging.info('added: ' + row['member'] + ' ' + str(r))
logging.info("script completed.  (start time: " + ct.strftime("%m/%d/%Y, %H:%M:%S") + ")")
