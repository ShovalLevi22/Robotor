import schedule
from CoreFuncs.resources import Myjson, log
from CoreFuncs.classes import Appoint
import threading
from telebot import types
import time
from datetime import datetime, timedelta
from CoreFuncs.func import goodloking_date, btn, AST, deleteByList, create_menu
from settings import DB, GC, bot, SetJs

MsgRem = Myjson("Files/text/AppoRemindMsg")


class SyncAndRemind:
    """ ['SyncAndRemind', 'function', appo_id, appo_version] """
    def __init__(self,call):

        self.call = call
        self.chat_id = str(call.from_user.id)
        self.value = AST(self.call)[3]  # will break if not exists #[appo_id,version]
        self.ap = Appoint(self.chat_id)
        is_exist = self.ap.setAppo(self.value)

        if not is_exist or self.ap.version != int(AST(self.call)[4]):
            self.not_relevant()

        else:
            self.ap.getUser(self.chat_id)
            method_name = AST(call)[2]
            method = getattr(self, method_name, lambda: 'Invalid')
            method()


    @staticmethod
    def hacky_init(call):
        SyncAndRemind(call)

    @staticmethod
    def activate():
        try:
            log.Info("'SyncAndRemind'",f"Starting 'activate' function. Thread:{threading.current_thread()}")
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
                            DB.update(table,f"date='{str(gcdate)}',version='{dbap.version + 1}'",f"appoint_id='{db['appoint_id']}'")
                            dbap.date = gcdate
                        if dbap.date < now:
                            DB.delete(table,f"appoint_id='{db['appoint_id']}'")
                        if dbap.time != str(gctime)[:5]:
                            DB.update(table,f"time='{gctime}',version='{dbap.version + 1}'",f"appoint_id='{db['appoint_id']}'")
                            dbap.time = str(gctime)[:5]

                        if table != "Admin_appoints" \
                                and now.weekday() != 5 \
                                and limit_date >= dbap.date > now\
                                and dbap.is_confirmed == 0:

                            if dbap.date == tomorrow:
                                txt = "מחר "
                            else:
                                txt = "בתאריך "+goodloking_date(str(dbap.date))

                            DB.update(table, f"is_confirmed={1}", f"appoint_id='{dbap.appo_id}'")
                            GC.update_color(dbap.appo_id, '5')
                            text = "היי, יש לך תור " + txt +"ל"+ dbap.serv_name + " בשעה " + dbap.time + " האם את/ה מאשרת את הגעתך?"
                            # log.Info(dbap.chat_id, f"bot send reminder to this user.\n vals: {dbap.serv_name},{goodloking_date(str(dbap.date))},{dbap.time},ap_id-{dbap.appo_id}, txt:{txt}")
                            bot.send_message(dbap.chat_id, text,
                                             reply_markup=SyncAndRemind.confirm_keyboard(dbap.appo_id, dbap.version),
                                             parse_mode='Markdown',disable_web_page_preview=True)
                            # MsgRem.addToLstInJson(dbap.chat_id,bot.send_message(dbap.chat_id,text,reply_markup=SyncAndRemind.confirm_keyboard(dbap.appo_id),parse_mode='Markdown',
                            #                                                     disable_web_page_preview=True).message_id)
        except:
            pass

    @staticmethod
    def confirm_keyboard(appo_id,ap_version):
        markup = types.InlineKeyboardMarkup()
        markup.add(btn("כן",['SyncAndRemind', 'yes', appo_id, ap_version]))
        markup.add(btn("לא - בטל את התור",['SyncAndRemind', 'no', appo_id, ap_version]))

        return markup

    def yes(self):
        GC.update_color(self.ap.appo_id,'2')
        txt = "בחירתך נקלטה בהצלחה!\n"
        bot.edit_message_text(txt,self.chat_id,self.call.message.message_id)
        time.sleep(1)
        bot.delete_message(self.chat_id,self.call.message.message_id)
        update_txt = '📌 אושרה הגעה ע"י ' + self.ap.cli_name + '\n ל' + self.ap.serv_name + "ב- " + goodloking_date(
            str(self.ap.date))
        bot.send_message(SetJs.get("Channels")["update"],update_txt)

    def no(self):
        GC.update_color(self.ap.appo_id,'11')
        text = "האם את/ה בטוח שאתה רוצה לבטל את התור?"
        return create_menu(self.call,text,self.cancelKeyboard())


    def cancelKeyboard(self):
      markup = types.InlineKeyboardMarkup()
      markup.add(btn("כן", ['SyncAndRemind', 'del_', self.ap.appo_id, self.ap.version]))
      markup.add(btn("לא-אני מאשר/ת את הגעתי", ['SyncAndRemind', 'yes', self.ap.appo_id, self.ap.version]))
      return markup

    def del_(self):
        txt = self.ap.delAppo()  # + "\n" + start_text(chat_id)
        # create_menu(call,str(txt),mainKeyboard(chat_id))
        bot.edit_message_text(txt,self.chat_id,self.call.message.message_id)
        time.sleep(1)
        # deleteByList(self.chat_id,MsgRem)
        bot.delete_message(self.chat_id,self.call.message.message_id)

    def not_relevant(self):
        create_menu(self.call, "תזכורת זו אינה רלוונטית,\n תשובתך *לא* נקלטה במערכת.", None)
        time.sleep(1)
        bot.delete_message(self.chat_id, self.call.message.message_id)


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