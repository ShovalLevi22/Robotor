from CoreFuncs.settings import *
from CoreFuncs.func import *
from CoreFuncs.classes import Appoint
from Processes.makeAppoint import All_MakeAppo
class All_MainMenu:
    '''
        ['All', 'MainMenu', 'num button']
    '''
    def __init__(self, call, init=False):

        self.call = call
        self.chat_id = str(call.from_user.id)
        self.value_from_callback = AST(call)[3] if not init else 0
        ActiveUsers.append(self.chat_id)
        method_name = 'Button_' + str(self.value_from_callback)
        log.Choice(self.chat_id,"main menu "+method_name)
        method = getattr(self, method_name, lambda: 'Invalid')
        # return method()
        method()
        ActiveUsers.remove(self.chat_id)

    #
    @staticmethod
    def hacky_init(call):
        All_MainMenu(call)

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
                return create_menu(self.call, ServsTexst, All_MakeAppo.serviceKeyboard())

    # Show active Appointments
    def Button_2(self):
        create_menu(self.call,textShowApp(self.chat_id,self.call),onlyToMainKeyboard())

    # Cancel active Appointments
    def Button_3(self):
        create_menu(self.call,textShowApp(self.call.message.chat.id,self.call),
                    cancelAPPKeyboard(self.call.message.chat.id))




class Keyborad_Switcher:
    '''
        [ Version, kb_name, Admin_func(opt)... ]
    '''

    def __init__(self, call):
        self.call = call
        kb_name = AST(call)[1]
        self.chat_id = str(call.from_user.id)
        method_name = AST(call)[2]
        method_name = globals()[f'{kb_name}_{method_name}']
        method = getattr(method_name, 'hacky_init', lambda: 'Invalid')
        method(call)

@bot.message_handler(commands=['start'])
def handle_command_start(message, text=''):
    chat_id = str(message.chat.id)
    log.In(chat_id)
    cleanInfo(chat_id)
    MsgJs.addToLstInJson(chat_id,message.message_id)

    try:

        if(checkRegistration(chat_id)):
            st_txt = start_text(chat_id)
            msg = bot.send_message(chat_id,text + '\n\n' + st_txt,
                                   reply_markup=mainKeyboard(chat_id),
                                   parse_mode='Markdown',
                                   disable_web_page_preview=True)


        else:  # '''UnRegister_txt'''
            msg = bot.send_message(chat_id,UnRegister_txt() + "\n\n* מה השם המלא שלך?*\n\n",
                                   parse_mode='Markdown')
            bot.register_next_step_handler(msg, process_name_step)

        deleteByList(chat_id)
        MsgJs.addToLstInJson(chat_id,msg.message_id)


    except:
        log.Warn(chat_id)
        FinalEx(chat_id)

# Handlers
@bot.callback_query_handler(func=lambda call: True)
def handle_all_button_clicks(call):
    chat_id = str(call.from_user.id)
    try:
        if (AST(call)[0] == Version):
            Keyborad_Switcher(call)
        else:
            VersionMisMatch(call)
    except:
        traceback.print_exc()
        print('chat id -', chat_id, 'in Menu -', AST(call)[1])


# Delete unnecessary messages
@bot.message_handler(content_types=['text', 'photo', 'video',
                                    'video_note', 'voice', 'contact',
                                    'sticker', 'location', 'document'])
def deleteMessage(message):
    if (message.chat.type == 'private'):
        bot.delete_message(message.chat.id, message.message_id)


bot.polling()