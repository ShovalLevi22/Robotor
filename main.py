from CoreFuncs.func import *
from CoreFuncs.classes import Appoint
from Processes.makeAppoint import MakeAppo, DelAppo
from CoreFuncs.Admin import Admin, Admin_Stock
from Processes.registration import Registration
from telebot.apihelper import ApiException
from CoreFuncs.resources import log
from Files.text.Headers import ServsTexst, AppoHead

class MainMenu:
    '''
        ['MainMenu', 'num button']
    '''
    def __init__(self, call, init=False):

        self.call = call
        self.chat_id = str(call.from_user.id)
        self.value_from_callback = AST(call)[2] if not init else 0
        method_name = 'Button_' + str(self.value_from_callback)
        log.Choice(self.chat_id, "main menu "+method_name)
        method = getattr(self, method_name, lambda: 'Invalid')
        try:
            method()
        except:
            log.Warn(self.chat_id)
            FinalEx(self.chat_id)

    @staticmethod
    def hacky_init(call):
        MainMenu(call)

    def Button_0(self):
        if not checkRegistration(self.chat_id):
            Registration.next_step_reg(self.chat_id)
        else:
            cleanInfo(self.chat_id)
            return create_menu(self.call, start_text(self.chat_id), mainKeyboard(self.chat_id))

    def Button_1(self):
        if self.chat_id in SetJs.get("Admins"):
            return create_menu(self.call,"על מנת לקבוע תור ללקוח נא שלח את איש הקשר לו תרצה לקבוע את התור",
                        onlyToMainKeyboard())
        else:
            if int(DB.getOneVal('Appointments', 'COUNT(*)', f"user_id='{self.chat_id}' ")) >= appoin_limit:
                txt = "*❗️ שים/י ❤️ הגעת למספר התורים המקסימלי שניתן לקבוע ולכן לא ניתן לקבוע תור חדש ❗️ \n\n*" + start_text(
                    self.chat_id)
                return create_menu(self.call, txt, mainKeyboard(self.chat_id))

            else:
                AppList[self.chat_id] = Appoint()
                AppList[self.chat_id].getUser(self.chat_id)
                TempUsers[self.chat_id] = []
                return create_menu(self.call, ServsTexst, MakeAppo.serviceKeyboard())

    # Show active Appointments
    def Button_2(self):
        if self.chat_id in SetJs.get("Admins"):

            msg = send_msg(self.chat_id, "על מנת לצפות בתורים עתידיים של לקוח נא שלח את איש הקשר,\n לחזרה לתפריט הראשי לחץ /start",)
            bot.register_next_step_handler(msg, Admin.textShowAppContact)
        else:
            create_menu(self.call, textShowApp(self.chat_id, self.call), onlyToMainKeyboard())

    # Cancel active Appointments
    def Button_3(self):
        if self.chat_id in SetJs.get("Admins"):
            create_menu(self.call, Admin.textShowAppAdmin(self.chat_id), DelAppo.cancelAPPKeyboard(self.chat_id))
        else:
            create_menu(self.call, textShowApp(self.chat_id, self.call),
                        DelAppo.cancelAPPKeyboard(self.chat_id))

    # change stock
    def Button_4(self):
        try:
            if Admin_Stock.text():
                text = "*רשימת השירותים הנוכחית:*\n\n" + Admin_Stock.print_stock(Admin_Stock.text())

            else:
                text = "לא קיימים שירותים.\n ניתן להכניס שירותים למאגר בלחיצה על 'שינוי רשימת השירותים'."
            create_menu(self.call, text, Admin_Stock.Keyboard())

        except ApiException:
            pass

    # send broad message
    def Button_5(self):
        msg = send_msg(self.chat_id, "נא שלח/י את הודעת התפוצה,\n לחזרה לתפריט הראשי לחץ/י /start", )
        bot.register_next_step_handler(msg, Admin.confirmSendBroadMsg)

    # open channels
    def Button_6(self):
        create_menu(self.call, optionsHead, Admin.chanelsKeyboard())


class Keyborad_Switcher:
    '''
        [ Version, kb_name, Admin_func(opt)... ]
    '''

    def __init__(self, call):
        self.call = call
        self.call_data = AST(call)
        kb_name = self.call_data[1]
        self.chat_id = str(call.from_user.id)
        method_name = globals()[f'{kb_name}']
        method = getattr(method_name, 'hacky_init', lambda: 'Invalid')
        log.Info(self.chat_id, f"call:{str(self.call_data)}")
        method(call)

@bot.message_handler(commands=['start'])
def handle_command_start(message):
    chat_id = str(message.chat.id)
    log.In(chat_id)
    cleanInfo(chat_id)
    MsgJs.addToLstInJson(chat_id, message.message_id)
    try:
        if(checkRegistration(chat_id)):
            mainMenu_msg(chat_id)
        else:
            Registration.next_step_reg(chat_id)
    except:
        log.Warn(chat_id)
        FinalEx(chat_id)

@bot.message_handler(content_types=['contact'])
def handle_contanct(message):
    chat_id = str(message.chat.id)
    if chat_id not in ActiveUsers:
        ActiveUsers.append(chat_id)
        log.In(chat_id)
        AppList[chat_id] = Appoint()
        ap = AppList[chat_id]
        phone = phone_Refactor(message.contact.phone_number)
        try:
            if str(chat_id) in SetJs.get('Admins'):
                MsgJs.addToLstInJson(chat_id,message.message_id)
                if not AppList[chat_id].getUserByPhone(phone):
                    ap.phone = phone
                ap.cli_name = message.contact.first_name
                ap.chat_id = chat_id
                addedText = 'קבע תור ל -\n *שם:*' + ap.cli_name + '\n*פלאפון: *' + ap.phone
                bot.delete_message(message.chat.id,message.message_id)
                send_msg(chat_id, addedText + '\n\n' + AppoHead, MakeAppo.serviceKeyboard())

            else:
              bot.delete_message(message.chat.id, message.message_id)

        except:
            log.Warn(chat_id)
            FinalEx(chat_id)
        finally:
            ActiveUsers.remove(chat_id)
    else:
        bot.delete_message(message.chat.id, message.message_id)

# Handlers
@bot.callback_query_handler(func=lambda call: AST(call)[0] == 'SyncAndRemind')
def handle_SyncAndRemind(call):
    chat_id = str(call.from_user.id)
    if chat_id not in ActiveUsers:
        ActiveUsers.append(chat_id)
        try:
            SyncAndRemind(call)
        except:
            log.Warn('handle_SyncAndRemind', f"user '{chat_id}' had problem with call:{AST(call)}")

        finally:
            ActiveUsers.remove(chat_id)

@bot.callback_query_handler(func=lambda call: AST(call)[0] == 'broad_msg')
def handle_broad_msg(call):
    bot.delete_message(str(call.from_user.id), call.message.message_id)


@bot.callback_query_handler(func=lambda call: True)
def handle_all_button_clicks(call):
    chat_id = str(call.from_user.id)
    if chat_id not in ActiveUsers:
        ActiveUsers.append(chat_id)
        try:

                if (AST(call)[0] == Version):
                    Keyborad_Switcher(call)
                else:
                    VersionMisMatch(call)
        except:
            log.Warn('handle_all_button_clicks', f"user '{chat_id}' had problem with call:{AST(call)}")

        finally:
            ActiveUsers.remove(chat_id)





# Delete unnecessary messages
@bot.message_handler(content_types=['text', 'photo', 'video',
                                    'video_note', 'voice', 'contact',
                                    'sticker', 'location', 'document'])
def deleteMessage(message):
    chat_id = str(message.chat.id)
    if not checkRegistration(chat_id):
        if chat_id in UserLists:
            bot.delete_message(message.chat.id, message.message_id)
        else:
            MsgJs.addToLstInJson(chat_id, message.message_id)
            Registration.next_step_reg(chat_id, "במהלך ההרשמה בוצע אתחול,\n יש להתחיל את תהליך ההרשמה פעם נוספת.\n")

    elif (message.chat.type == 'private'):
        bot.delete_message(chat_id, message.message_id)




import threading
from Processes.syncAndRemind import SyncAndRemind, schedual
# thread = threading.Thread(target=SyncAndRemind.activate)
thread = threading.Thread(target=schedual)
thread.start()

bot.polling()
