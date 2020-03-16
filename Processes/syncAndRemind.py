import schedule
from CoreFuncs.resources import Myjson
from CoreFuncs.classes import Appoint
import threading
from telebot import types

from datetime import datetime, timedelta, time
from CoreFuncs.func import goodloking_date, btn, AST, deleteByList, create_menu
from settings import DB, GC, bot, ActiveUsers, SetJs
MsgRem = Myjson("Files/text/AppoRemindMsg")


class SyncAndRemind:
    """ ['SyncAndRemind', 'function', value] """
    def __init__(self,call):

        self.call = call
        self.chat_id = str(call.from_user.id)
        ActiveUsers.append(self.chat_id)
        self.value = AST(self.call)[3]  # will break if not exists
        self.ap = Appoint(self.chat_id)
        self.ap.setAppo(self.value)
        self.ap.getUser(self.chat_id)

        method_name = AST(call)[2]
        method = getattr(self,method_name,lambda: 'Invalid')
        method()
        ActiveUsers.remove(self.chat_id)


    @staticmethod
    def hacky_init(call):
        SyncAndRemind(call)

    @staticmethod
    def activate():
        print("in sync")
        print(threading.current_thread())
        dbap = Appoint()
        now = datetime.utcnow().date()
        tomorrow = (now + timedelta(days=7))
        limit_date = tomorrow
        if now.weekday() == 4:  # if  its friday
            limit_date = limit_date + timedelta(days=1)

        for table in ["Appointments","Admin_Appoints"]:
            appos = DB.get(table)
            for i, db in appos.iterrows():
                dbap.setAppo(db["appoint_id"])
                dbap.date = datetime.strptime(dbap.date, "%Y-%m-%d").date()
                gc = GC.getAppo(db["appoint_id"])
                if gc["status"] == 'canceled':
                    DB.delete(table,f"appoint_id='{db['appoint_id']}'")
                else:
                    date = datetime.strptime(gc["start"]["dateTime"][:19], '%Y-%m-%dT%H:%M:%S')
                    gcdate = date.date()   #gc["start"]["dateTime"][:10]
                    gctime = date.time() #gc["start"]["dateTime"][11:19]
                    if dbap.date != gcdate:
                        DB.update(table,f"SET date='{str(gcdate)}'",f"appoint_id='{db['appoint_id']}'")
                        dbap.date = gcdate
                    if dbap.date < now:
                        DB.delete(table,f"appoint_id='{db['appoint_id']}'")
                    if dbap.time != str(gctime)[:5]:
                        DB.update(table,f"SET time='{gctime}'",f"appoint_id='{db['appoint_id']}'")
                        dbap.time = str(gctime)[:5]

                    if table != "Admin_appoints" and now.weekday() != 5:  # if not admin appo and its not saturday
                        if dbap.date <= limit_date and dbap.date > now:
                            if dbap.date == tomorrow:
                                txt = "היי, יש לך תור מחר ל"
                            else:
                                txt = "היי, יש לך תור בתאריך "+goodloking_date(str(dbap.date))+" ל"

                            GC.update_color(dbap.appo_id,'5')
                            text = txt + dbap.serv_name + " בשעה " + dbap.time + " האם את/ה מאשרת את הגעתך?"
                            MsgRem.addToLstInJson(dbap.chat_id,bot.send_message(dbap.chat_id,text,reply_markup=SyncAndRemind.confirm_keyboard(dbap.appo_id),parse_mode='Markdown',
                                                                                disable_web_page_preview=True).message_id)

    @staticmethod
    def confirm_keyboard(appo_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(btn("כן",['SyncAndRemind', 'yes_conf',appo_id]))
        markup.add(btn("לא - בטל את התור",['SyncAndRemind', 'no_conf',appo_id]))
        # markup.add(types.InlineKeyboardButton(text="כן", callback_data="['" + Version + "','reminder','1','"+appoint_id+"']"))
        # markup.add(types.InlineKeyboardButton(text="לא - בטל את התור", callback_data="['" + Version + "','reminder','2','"+appoint_id+"']"))
        return markup

    def yes_conf(self):
        GC.update_color(self.ap.appo_id,'2')
        txt = "בחירתך נקלטה בהצלחה!\n"
        bot.edit_message_text(txt,self.chat_id,self.call.message.message_id)
        time.sleep(1)
        deleteByList(self.chat_id,MsgRem)
        update_txt = '📌 אושרה הגעה ע"י ' + self.ap.cli_name + '\n ל' + self.ap.serv_name + "ב- " + goodloking_date(
            str(self.ap.date))
        bot.send_message(SetJs.get("Channels")["update"],update_txt)

    def no_conf(self):
        GC.update_color(self.appo_id,'11')
        text = "האם את/ה בטוח שאתה רוצה לבטל את התור?"
        return create_menu(self.call,text,self.cancelKeyboard(self.ap.appo_id))


    def cancelKeyboard(self, appo_id):
      markup = types.InlineKeyboardMarkup()
      markup.add(btn("כן",['SyncAndRemind','yes_conf',appo_id]))
      markup.add(btn("לא-אני מאשר/ת את הגעתי",['SyncAndRemind','yes_conf',appo_id]))

      # markup.add(types.InlineKeyboardButton(text='כן', callback_data="['"+Version+"','reminder','3','"+appo_id+"']"))
      # markup.add(types.InlineKeyboardButton(text='לא-אני מאשר/ת את הגעתי', callback_data="['"+Version+"','reminder','1','"+appo_id+"']"))
      return markup

    def yes_del(self):
        txt = self.ap.delAppo()  # + "\n" + start_text(chat_id)
        # create_menu(call,str(txt),mainKeyboard(chat_id))
        bot.edit_message_text(txt,self.chat_id,self.call.message.message_id)
        time.sleep(1)
        deleteByList(self.chat_id,MsgRem)

# SyncAndRemind.activate()

# def schedual():
#     schedule.every().day.at("08:00").do(SyncAndRemind.activate())
#
#     while True: #BUG: busy wait?
#          schedule.run_pending()
#          time.sleep(120) # wait 2 minutes
#
#
# thread = threading.Thread(target=schedual)
# thread.start()
#
# thread = threading.Thread(target=SyncAndRemind.activate())
# thread.start()