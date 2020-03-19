from CoreFuncs.func import *
from CoreFuncs.classes import Appoint
from Processes.makeAppoint import MakeAppo, DelAppo
from CoreFuncs.Admin import Admin, Admin_Stock
from Processes.registration import Registration
from telebot.apihelper import ApiException
from CoreFuncs.resources import log
import time
class MainMenu:
    '''
        ['MainMenu', 'num button']
    '''
    def __init__(self, call, init=False):

        self.call = call
        self.chat_id = str(call.from_user.id)
        self.value_from_callback = AST(call)[2] if not init else 0
        method_name = 'Button_' + str(self.value_from_callback)
        log.Choice(self.chat_id,"main menu "+method_name)
        method = getattr(self, method_name, lambda: 'Invalid')
        # return method()
        method()

    @staticmethod
    def hacky_init(call):
        MainMenu(call)

    def Button_0(self):
        cleanInfo(self.chat_id)
        return create_menu(self.call,start_text(self.chat_id),mainKeyboard(self.chat_id))

    def Button_1(self):
        if self.chat_id in SetJs.get("Admins"):
            return create_menu(self.call,"על מנת לקבוע תור ללקוח נא שלח את איש הקשר לו תרצה לקבוע את התור",
                        onlyToMainKeyboard())
        else:
            if int(DB.getOneVal('Appointments','COUNT(*)',f"user_id='{self.chat_id}' ")) >= appoin_limit:
                txt = "*❗️ שים/י ❤️ הגעת למספר התורים המקסימלי שניתן לקבוע ולכן לא ניתן לקבוע תור חדש ❗️ \n\n*" + start_text(
                    self.chat_id)
                return create_menu(self.call, txt, mainKeyboard(self.chat_id))

            else:
                AppList[self.chat_id] = Appoint()
                AppList[self.chat_id].getUser(self.chat_id)
                return create_menu(self.call, ServsTexst, MakeAppo.serviceKeyboard())

    # Show active Appointments
    def Button_2(self):
        if self.chat_id in SetJs.get("Admins"):
            deleteByList(self.chat_id)
            msg = bot.send_message(chat_id=self.chat_id,
                                   text="על מנת לצפות בתורים עתידיים של לקוח נא שלח את איש הקשר,\n לחזרה לתפריט הראשי לחץ /start",
                                   parse_mode='Markdown')
            MsgJs.addToLstInJson(self.chat_id,msg.message_id)
            bot.register_next_step_handler(msg,Admin.textShowAppContact)

        else:
            create_menu(self.call,textShowApp(self.chat_id,self.call),onlyToMainKeyboard())

    # Cancel active Appointments
    def Button_3(self):
        if self.chat_id in SetJs.get("Admins"):
            create_menu(self.call,Admin.textShowAppAdmin(self.chat_id),DelAppo.cancelAPPKeyboard(self.chat_id))
        else:
            create_menu(self.call,textShowApp(self.chat_id,self.call),
                        DelAppo.cancelAPPKeyboard(self.chat_id))

    # change stock
    def Button_4(self):
        try:
            text = 'קידוד השירותים בפורמט -\n'
            text += "`שם השירות - זמן התור - מחיר `" + '\n\n'
            text += 'קידוד שירותים בפורמט באנגלית- (אותו דבר רק מראה)\n'
            text += "`service name - duration - Price`" + '\n\n'
            MsgJs.addToLstInJson(self.chat_id,bot.edit_message_text(chat_id=self.chat_id,
                                                               text=text,
                                                               message_id=self.call.message.message_id,
                                                               parse_mode='Markdown',
                                                               disable_web_page_preview=True).message_id)
            MsgJs.addToLstInJson(self.chat_id,bot.send_message(chat_id=self.chat_id,
                                                          text=Admin_Stock.text(),
                                                          reply_markup=Admin_Stock.Keyboard(),
                                                          parse_mode='Markdown',
                                                          disable_web_page_preview=True).message_id)
        except ApiException:
            pass

    # send broad message
    def Button_5(self):
        deleteByList(str(self.chat_id))
        msg = bot.send_message(chat_id=self.chat_id,
                               text="נא שלח/י את הודעת התפוצה,\n לחזרה לתפריט הראשי לחץ /start",
                               parse_mode='Markdown')
        MsgJs.addToLstInJson(self.chat_id,msg.message_id)
        bot.register_next_step_handler(msg,Admin.confirmSendBroadMsg)

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

        else:  # '''UnRegister_txt'''
            # msg = bot.send_message(chat_id,txtFromFile('UnregisteredTXT') + "\n\n* מה השם המלא שלך?*\n\n",
            #                        parse_mode='Markdown')
            Registration.next_step_reg(chat_id)
            # bot.register_next_step_handler(msg, Registration, 'process_name_step')
            #
            # deleteByList(chat_id)
            # MsgJs.addToLstInJson(chat_id,msg.message_id)


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
                deleteByList(chat_id)
                MsgJs.addToLstInJson(chat_id,bot.send_message(chat_id,text=addedText + '\n\n' + AppoHead,
                                                              reply_markup=MakeAppo.serviceKeyboard(),parse_mode='Markdown',
                                                              disable_web_page_preview=True).message_id)
            else:
              bot.delete_message(message.chat.id, message.message_id)

        except:
            log.Warn(chat_id)
            FinalEx(chat_id)
        finally:
            ActiveUsers.remove(chat_id)
    else:
        bot.delete_message(message.chat.id,message.message_id)

# Handlers
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
            log.Warn('handle_all_button_clicks',f"user '{chat_id}' had problem with call:{AST(call)}")

        finally:
            ActiveUsers.remove(chat_id)





# Delete unnecessary messages
@bot.message_handler(content_types=['text', 'photo', 'video',
                                    'video_note', 'voice', 'contact',
                                    'sticker', 'location', 'document'])
def deleteMessage(message):
    if (message.chat.type == 'private'):
        bot.delete_message(message.chat.id, message.message_id)

import threading
from Processes.syncAndRemind import SyncAndRemind
thread = threading.Thread(target=SyncAndRemind.activate)
thread.start()

bot.polling()
