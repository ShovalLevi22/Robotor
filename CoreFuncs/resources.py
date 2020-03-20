# from CoreFuncs.func import goodloking_date
from threading import Lock
import json
import traceback
import logging
import sqlite3
import pandas as pd
import os.path
import pickle
from googleapiclient.discovery import build
# from CoreFuncs.func import FinalEx


class Log():
    def __init__(self):
        logging.basicConfig(filename='bot.log',filemode='w',format='%(asctime)s - %(message)s',level=logging.INFO)
        self.func_name = traceback.extract_stack(None,2)[0][2]

    def Pass(self,identifier):
        logging.error(str(identifier) + f":Pass exception occurred in " + self.func_name + f" -> {traceback.format_exc()}")
        # logging.info((chat_id + f":Pass exception occurred in " + self.func_name))

    def Warn(self,identifier='Unknown',msg=' '):
        logging.warning(str(identifier) + ": " + f"An Unexcepted error occurred in " + self.func_name + ". " + msg + "-> ",
                        exc_info=True)

    def Info(self, identifier, txt):
        logging.info(identifier + ": " + txt)

    def In(self,chat_id: object) -> object:
        logging.info(str(chat_id) + ": in " + self.func_name)

    def Choice(self,chat_id,txt):
        logging.info(chat_id + ": Action: " + txt)


log = Log()


class wrapper:
    def __init__(self, activator='Unknown'):
        self.mutex = Lock()
        self.activator = activator

    def wrap(self, pre, post):
        def decorate(func):
            def call(*args, **kwargs):
                pre(self, func, *args, **kwargs)
                try:
                    # logging.info(f"function {self.activator}.{func.__name__} activated")
                    # log.Info(self.activator, f"activate func '{func.__name__}'")
                    result = func(*args, **kwargs)
                except:
                    logging.warning(str(self.activator) + f": func:{func.__name__}, args:{args[1:]},\n kwargs:{kwargs}->\n ",
                                    exc_info=True)

                    # log.Warn(self.activator,f"func:{func.__name__}, args:{kwargs}")
                post(self, func, *args, **kwargs)
                return result

            return call

        return decorate

    def trace_in(self, func, *args, **kwargs):
        self.mutex.acquire(1)

    def trace_out(self, func, *args, **kwargs):
        self.mutex.release()


class Myjson:
    w = wrapper("Myjson")

    def __init__(self, file_path):
        self.file = file_path + '.json'

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def get(self,key=False):
        with open(self.file, encoding='utf-8') as json_file:
            data = json.loads(json_file.read(), encoding='utf-8')
            if not key:
                return data
            elif key in data:
                val = data[key]
                return val
            return None

    @wrapper.wrap(w,w.trace_in,w.trace_out)
    def addToLstInJson(self, key, value):
        key = str(key)
        with open(self.file,encoding='utf-8') as json_file:
            data = json.loads(json_file.read(), encoding='utf-8')
            data.setdefault(key, []).append(value)
        with open(self.file,'w') as outfile:
            json.dump(data,outfile,ensure_ascii=False)

    @wrapper.wrap(w, w.trace_in,w.trace_out)
    def delVal(self, key):
        with open(self.file) as json_file:
            data = json.load(json_file)
            data.pop(key, None)

        with open(self.file, 'w') as outfile:
            json.dump(data,outfile)


class DBgetset:
    w = wrapper("DBgetset")

    def __init__(self,db_name):
        self.connection = sqlite3.connect(db_name,check_same_thread=False)
        self.c = self.connection.cursor()

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def get(self, table, select='*', where=1, order=1):
        SQL_Query = pd.read_sql_query(f"SELECT {select} FROM {table} WHERE {where} ORDER BY {order}",self.connection)
        return SQL_Query

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def delete(self, table, where):  # BUG function isnt ready
        try:
            self.c.execute(f"DELETE FROM {table} WHERE {where}")
            self.connection.commit()
            return True
        except:
            return False

    @wrapper.wrap(w,w.trace_in,w.trace_out)
    def insert(self, table, columns, values):  # BUG function isnt ready
        # self.c.execute(f"INSERT INTO {table} VALUES ({values})")
        self.c.execute(f"INSERT INTO {table} ({columns}) VALUES ({values})")
        self.connection.commit()

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def update(self, table, set, where,):  # BUG function isnt ready
        # log.Info()
        self.c.execute(f"UPDATE {table} SET {set} WHERE {where}")
        self.connection.commit()

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def getOneVal(self, table, select, where=1):
        self.c.execute(f"SELECT {select} FROM {table} WHERE {where}")
        res = self.c.fetchall()
        if res == []:
            return False
        return (res[0][0])


class GCFuncs:
    w = wrapper("GCFuncs")

    def __init__(self):
        self.service = self.get_calendar_service()

    @wrapper.wrap(w,w.trace_in, w.trace_out)
    def addAppo(self, start, end, summary, description):

        try:
            event_result = self.service.events().insert(calendarId='primary',
                                                        body={
                                                            "summary": summary,
                                                            "description": description,
                                                            "start": {"dateTime": start,"timeZone": "Asia/Jerusalem"},
                                                            "end": {"dateTime": end,"timeZone": "Asia/Jerusalem"},
                                                        }
                                                        ).execute()
            return event_result
        except:
            # log.Warn('Unknown',
            #            'arguments:\n summary: ' + summary + '\n description: ' + description + '\n start: ' + ap.start + '\n end: ' + ap.end + '\n')
            pass

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def getAppo(self, appo_id):

        try:
            events = self.service.events().get(calendarId='primary',eventId=appo_id).execute()
            return events
        except:
            # log.Pass(str(chat_id))
            pass

    @wrapper.wrap(w,w.trace_in, w.trace_out)
    def getAppoList(self, start, end):
        try:
            events_result = self.service.events().list(calendarId='primary',timeMin=start,timeMax=end,
                                                       maxResults=100,singleEvents=True,
                                                       orderBy='startTime').execute()
            return events_result
        except:
            # Log().Pass(str(chat_id))
            pass

    @wrapper.wrap(w, w.trace_in, w.trace_out)
    def delAppo(self, appo_id):

        try:
            events = self.service.events().delete(calendarId='primary',eventId=appo_id).execute()
            return events
        except:
            # Log().Pass(str(chat_id))
            pass

    @wrapper.wrap(w,w.trace_in,w.trace_out)
    def addMail(self,appo_id,email):
        self.service.events().patch(calendarId='primary',eventId=appo_id,body={"attendees": [
            {"email": [email]}]},).execute()

    @wrapper.wrap(w,w.trace_in,w.trace_out)
    def update_color(self,appo_id,color):
        try:
            self.service.events().patch(
                calendarId='primary',
                eventId=appo_id,
                body={'colorId': color},).execute()
        except:
            print('Could not update color')
            # traceback.print_exc()

    def get_calendar_service(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("Files/shovalleviw.pickle"):  # outputJson('MailToken')):
            with open("Files/shovalleviw.pickle",'rb') as token:
                creds = pickle.load(token)
        try:
            service = build('calendar','v3',credentials=creds)
        except:
            return 0

        return service
