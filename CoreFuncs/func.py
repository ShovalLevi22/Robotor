import ast
from settings import *
from datetime import datetime
from Files.text.Headers import *
from telebot import types
#Helpers:
def VersionMisMatch(call):
    try:
        # deleteByList(str(call.message.chat.id))
        MsgJs.addToLstInJson(str(call.message.chat.id) ,bot.edit_message_text(chat_id=call.message.chat.id,
                              text="*היי* 🤩\n הבוט עבר עדכון קטן \n אנא לחץ על על הכפתור על מנת לפתוח את התפריט המעודכן ביותר",
                              message_id=call.message.message_id,reply_markup=onlyToMainKeyboard(), parse_mode='Markdown').message_id)

    except:
        log.Pass(call.message.chat.id)
        pass

def AST(call):
    try:
        return ast.literal_eval(call.data)
    except:
        traceback.print_exc()
        return ['0', '0']

# def addToList(List, Key, newValue):
#     newValue = str(newValue)
#     try:
#         tempoList = []
#         for value in str(List[Key]).split(','):
#             tempoList.append(value)
#         tempoList.append(newValue)
#         myString = ",".join(tempoList)
#         List[Key] = myString
#     except KeyError:
#         List[Key] = newValue

def addToList(List, Key, newValue):
    newValue = str(newValue)
    try:
        if Key in List:
            List[Key].append(newValue)
        else:
            List[Key] = [newValue]
    except:
        log.Warn(Key)
        FinalEx()

def goodloking_date(str_date):
    try:
        date = datetime.strptime(str_date, '%Y-%m-%d')
        day = date.weekday()
        txtday = datetime.strftime(date,"%d.%m.%y") +" יום-"+ WeekDays[day]

        return txtday
    except:
        return 'Error'

def cleanInfo(chat_id):
    AppList.pop(chat_id, None)
    UserLists.pop(chat_id, None)
    TempLongList.pop(chat_id, None)
    StockChange.pop(chat_id, None)
    TempUsers.pop(str(chat_id),None)

    # ActiveUsers.remove(chat_id)

def checkRegistration(chat_id):
    if chat_id in SetJs.get("Admins"):
        return True
    try:
        count = DB.getOneVal('userdetails', 'COUNT(1)', f"user_id ='{chat_id}'")
        if count == 1:
            return True
        else:
            return False
    except:
        log.Warn(chat_id)
        FinalEx(chat_id)

def deleteByList(chat_id, MsgLst = MsgJs): #BUG: msgList is not optionall, to fix after fixing registration
    try:
        msgList = MsgLst.get()
        for value in msgList[str(chat_id)]:
                try:
                    bot.delete_message(chat_id, value)
                except Exception as d:
                    # log.Pass(chat_id)
                    pass
        try:
            MsgLst.delVal(chat_id)
        except Exception as d:
            log.Pass(chat_id)
            pass
    except KeyError:
        log.Pass(chat_id)
        pass

def FinalEx(chat_id):
    deleteByList(chat_id)
    log.In(chat_id)
    cleanInfo(chat_id)
    # ActiveUsers.remove(chat_id)
    log.Info(chat_id,'Information of user deleted from lists before new menu')
    markup =types.InlineKeyboardMarkup()
    if checkRegistration(chat_id):
        markup.add(btn(Home=True))
    else:
        markup.add(btn("חזרה לתפריט הראשי",['Registration','process_name_step']))
    text = 'נתקלת בבעיה, אנא לחץ על על הכפתור על מנת להתחיל את התהליך מחדש,\n '
    deleteByList(chat_id)
    MsgJs.addToLstInJson(chat_id,bot.send_message(chat_id=chat_id,
                                                                       text=text,
                                                                       reply_markup=markup,
                                                                       parse_mode='Markdown').message_id)

def startTime(date):
    try:
        date = datetime.strptime(str(date), '%Y-%m-%d')
        day = date.weekday()
        return DB.getOneVal('WorkTime',select= 'start', where=f"day_num='{day}'")
    except:
        print('Couldnt get startTime')
        traceback.print_exc()

def endTime(date):
    try:
        date = datetime.strptime(str(date), '%Y-%m-%d')
        day = date.weekday()
        return DB.getOneVal('WorkTime',select='end',where=f"day_num='{day}'")
    except:
        print('Couldnt get endTime')
        traceback.print_exc()

def check_if_exist(chat_id):
    try:
        if str(chat_id) in SetJs.get('Admins'):
            appoints = DB.get("Admin_appoints")

        else:
            appoints = DB.get("Appointments",where=f"user_id='{chat_id}'")

        for i,ap in appoints.iterrows():
            appo_id = ap["appoint_id"]
            events = GC.getAppo(appo_id)
            # בדיקת שעה תאריך
            if events['status'] == 'cancelled':
                DB.delete(appoints.table, where=f"appoint_id='{appo_id}'")
            else:
                date = str(events['start'].get('dateTime'))[:10]
                time = str(events['start'].get('dateTime'))[11:19]
                if date != ap["date"]:
                    DB.update(appoints.table,f"date='{date}'",f"appoint_id='{appo_id}'")

                if time != ap["time"]:
                    DB.update(appoints.table,f"time='{time}'",f"appoint_id='{appo_id}'")

    except:
        log.Warn(chat_id)
        return True

def phone_Refactor(phoneNumber):
    temp = phoneNumber.strip('+')
    if (temp[0:3] == '972'):
        temp = '0' + temp[3:]
    return temp



#Text:
def txtFromFile(jsonValue):
    try:
        f = open("Files/text/"+SetJs.get('TXT')[jsonValue]+".txt","r", encoding="utf8")
        x = f.read()
        f.close()
        return x
    except:
        log.Warn('System')

def start_text(chat_id):
    if chat_id in SetJs.get("Admins"):
        names = SetJs.get("Admins_name")
        txt = f"*היי {names[chat_id]}*" #"היי "  +names[chat_id]+"\n"

        return txt + admin_start_txt
    else:
        try:
            name = DB.getOneVal('userdetails','customer_name',f"user_id='{chat_id}'")
            namelist = name.split()
            txt = "*" + "היי " + namelist[0] + "*" + txtFromFile('Menu') + "\n" + instagram()
            return txt + optionsHead
        except IndexError:
            log.Warn(chat_id)
            print('no user')
            return 'Backup start text'
            #BAG: go to registration
        except:
            log.Warn(chat_id)
            FinalEx(chat_id)
            return 'Backup start text' #BAG: is this the right thing to do? need to check if user is registered

def instagram():
    if SetJs.get('InstagramAllow') == '1':
        text = "_אפשר גם לקבל רעיונות מהאינסטגרם שלי 👈 _"+\
               '[בקישור הזה]('+SetJs.get("InstagramLink")+')'+"\n\n"
        return text

    else:
        return ' '

#Keyboards:
def btn(text=None, callback_data=None, link=None, Ver=True, Home=False, Dummy=False):
    if Home:
        return btn('חזרה לתפריט הראשי', ['MainMenu', '0'])
    if Dummy:
        return btn(text, ['Dummy_Button'])
    if callback_data:
        callback_data.insert(0, Version) if Ver else None
        callb =  "['"
        for value in callback_data:
            callb += str(value)+"','"
        callb = callb[:-3] + "']"
        return types.InlineKeyboardButton(text=text, callback_data=callb)
    elif link:
        return types.InlineKeyboardButton(text=text, url='https://t.me/' + link)

def mainMenu_msg(chat_id,text=' '):
    deleteByList(chat_id)
    msg = bot.send_message(chat_id,text + '\n\n' + start_text(chat_id),
                           reply_markup=mainKeyboard(chat_id),
                           parse_mode='Markdown',
                           disable_web_page_preview=True)
    MsgJs.addToLstInJson(chat_id,msg.message_id)

def create_menu(call, text1, reply_m, string='default'):
    chat_id = str(call.from_user.id)
    try:

        if (string == 'default'):
            Text = text1
        else:
            Text = string + '\n\n' + text1
        bot.edit_message_text(chat_id=chat_id,
                              text=Text,
                              message_id=call.message.message_id,
                              reply_markup=reply_m,
                              parse_mode='Markdown',
                              disable_web_page_preview=True)
    except telebot.apihelper.ApiException:
        log.Pass(chat_id)
        pass

    except:
        log.Warn(chat_id)
        FinalEx(chat_id)

def send_msg(chat_id, text, reply_m = None, delete = True):
    msg = bot.send_message(chat_id,text,reply_markup=reply_m, parse_mode='Markdown',
                           disable_web_page_preview=True)
    if delete:
        deleteByList(chat_id)
    MsgJs.addToLstInJson(chat_id,msg.message_id)
    return msg

def mainKeyboard(chat_id):
    markup = types.InlineKeyboardMarkup()
    # Admin Panel
    if str(chat_id) in SetJs.get('Admins'):
        markup.add(types.InlineKeyboardButton(text=" קביעת תור ללקוח 📆", callback_data="['" + Version + "','Admin','1']")), \
        markup.add(types.InlineKeyboardButton(text=" צפייה בתורים עתידיים 📖", callback_data="['" + Version + "','Admin','6']")), \
        markup.add(types.InlineKeyboardButton(text=" ביטול תור עתידי ✖️", callback_data="['" + Version + "','Admin','2']")), \
        markup.add(types.InlineKeyboardButton(text=" פרטי השירותים שלי ✍", callback_data="['" + Version + "','Admin','3']")), \
        markup.add(types.InlineKeyboardButton(text=" שליחת הודעת תפוצה 📨", callback_data="['" + Version + "','Admin','7']")), \
        markup.add(types.InlineKeyboardButton(text=" ערוצים ↖️", callback_data="['" + Version + "','Admin','8']"))#, \

    else:
        # main buttons
        markup = types.InlineKeyboardMarkup()
        mainbut1 = "קביעת תור 📆"
        mainbut2 = "צפייה בתורים עתידיים 📖"
        mainbut3 = "ביטול תור עתידי ✖️"
        mainbut4 = "לוח  הודעות ✉️"
        mainbut5 = "מדריך לשימוש בבוט ⚙"
        markup.add(btn(mainbut1,["MainMenu",'1']))
        markup.add(btn(mainbut2,["MainMenu",'2']))
        markup.add(btn(mainbut3,["MainMenu",'3']))
        markup.add(btn(mainbut4,link="https://t.me/joinchat/AAAAAEwLLrdnXBfqXMAzfA"))
        markup.add(btn(mainbut5,link='http://t.me/MegaKush'))

    return markup

def onlyToMainKeyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(btn("חזרה לתפריט הראשי 🏠",['MainMenu', '0']))
    return markup

def textShowApp(chat_id, call):
    try:
        check_if_exist(chat_id) #check if the appoints are stil in the calendar
        result = DB.get('Appointments',where=f"user_id='{chat_id}'",order='date, time')
        chosen_chois = AST(call)[2]
        text = "\n"
        if result.empty:
            text += '\n\n אין תורים עתידיים להצגה, ניתן לקבוע תור דרך התפריט הראשי'
        elif chosen_chois == '3':
            text = "נא בחר/י תור לביטול:"
        else:
            for i, ap in result.iterrows():
                text +='תור ל' + ap["service_name"] + ' נקבע לתאריך ' + goodloking_date(ap["date"]) + ' בשעה ' + ap["time"][:5] + "\n\n"
            text += ' כל השעות ע"פ שעון 24 שעות.'
        return text
    except:
        log.Warn(chat_id)
        FinalEx(chat_id)

# def cancelAPPKeyboard(chat_id):
#     try:
#         appoints = DB.get("Appointments",where=f"user_id={chat_id}",order="date, time")
#         markup = types.InlineKeyboardMarkup()
#         for i,ap in appoints.iterrows():
#             text = ap["service_name"] + ' ב- ' + goodloking_date(ap["date"]) + ' ,' + ap["time"][:5]
#             markup.add(btn(text,['All','DelAppo','to_confirm_del_keyboard',str(ap["appoint_id"])]))
#
#             markup.add(
#                 types.InlineKeyboardButton(text=text,callback_data="['" + Version + "','delete','" + str(
#                     ap["appoint_id"]) + "']"))
#     except:
#         pass
#
#     markup.add(
#         types.InlineKeyboardButton(text="חזרה לתפריט הראשי 🏠",callback_data="['" + Version + "','Menu','0']"))
#     return markup

def confirmDelKeyboard(appo_indexer=None):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='כן', callback_data="['" + Version + "','confirm','yesdel','" + appo_indexer + "']"))
    markup.add(types.InlineKeyboardButton(text='לא',callback_data="['" + Version + "','Menu','0']"))
    return markup