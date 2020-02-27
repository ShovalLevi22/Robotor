import uuid
# from CoreFuncs.func import *
import telebot
from CoreFuncs.resources import *

MsgJs = Myjson("Files/Msgs")
SetJs = Myjson("Files/settings")
API_TOKEN = SetJs.get('Token')
bot = telebot.TeleBot(API_TOKEN)
Version = str(uuid.uuid4()).split('-')[1]
DB = DBgetset(SetJs.get('DB'))
GC = GCFuncs()

ActiveUsers = []
AppList = {} # contain class appoint
UserLists = {} # for registration, contain class client
TempLongList = {} #for how long
TempUsers = {}
StockChange = {}
BroadMessage = {}
appoin_limit = 3
WeekDays = ["ב'","ג'","ד'","ה'","ו'","ש'","א'",]
