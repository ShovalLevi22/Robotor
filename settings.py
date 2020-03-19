import uuid
# from CoreFuncs.func import *
import telebot
from CoreFuncs.resources import Myjson, DBgetset, GCFuncs
from datetime import timedelta
from collections import defaultdict

MsgJs = Myjson("Files/Msgs")
SetJs = Myjson("Files/settings")
API_TOKEN = SetJs.get('Token')
bot = telebot.TeleBot(API_TOKEN)
Version = str(uuid.uuid4()).split('-')[1]
DB = DBgetset(SetJs.get('DB'))
GC = GCFuncs()

ActiveUsers = []
AppList = {} # contain class appoint
UserLists = defaultdict(lambda: []) # for registration, contain class client Client()
TempLongList = {} #for how long
TempUsers = defaultdict(lambda: [])
# TempUsers = {}
StockChange = {}
BroadMessage = {}
appoin_limit = 3
WeekDays = ["ב'","ג'","ד'","ה'","ו'","ש'","א'",]
cancel_limit = timedelta(hours=1)


def changeVersion():
    global Version
    Version = str(uuid.uuid4()).split('-')[1]