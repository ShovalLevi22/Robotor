
import re
from settings import MsgJs, bot, DB
from CoreFuncs.func import AST, txtFromFile, deleteByList, btn, send_msg, start_text, mainKeyboard
from CoreFuncs.classes import Client
from telebot import types
from Files.text.Headers import endOFReg
from settings import UserLists, SetJs
from CoreFuncs.resources import log
import time

class Registration:
    """ ['function'] """
    def __init__(self, message, method_name):

        self.message = message
        self.chat_id = str(message.chat.id)
        self.cli = UserLists[self.chat_id]
        self.un_regi_txt = txtFromFile('UnregisteredTXT')
        method = getattr(self,method_name,lambda: 'Invalid')
        method()

    """ ['Registration', 'function'] """
    @staticmethod
    def hacky_init(call):
        method_name = AST(call)[2]
        Registration(call.message, method_name)

    @staticmethod
    def next_step_reg(chat_id, txt=""):
        txt += txtFromFile('UnregisteredTXT') + "\n\n* מה השם המלא שלך?*\n\n"
        msg = send_msg(chat_id, txt)
        bot.register_next_step_handler(msg, Registration, 'process_name_step')
        #
        # msg = bot.send_message(chat_id, txt,parse_mode='Markdown')
        # deleteByList(chat_id)
        # MsgJs.addToLstInJson(chat_id,msg.message_id)

    def process_name_step(self):
        MsgJs.addToLstInJson(self.chat_id,self.message.message_id)

        if (self.message.content_type == 'text'):
            if (self.message.text == '/start') or (self.message.text == '/חדש'):
                # time.sleep(0.01)
                self.next_step_reg(self.chat_id)
            else:
                UserLists[self.chat_id] = Client()
                self.cli = UserLists[self.chat_id]
                self.cli.cli_name = self.message.text
                msg = send_msg(self.chat_id,"מה מספר הפלאפון שלך?", delete=False)
                bot.register_next_step_handler(msg,self.process_number_step)
        else:
            msg = send_msg(self.chat_id,"אנא השתמשו בטקסט בלבד,\n רשמו את השם המלא שלכם",delete=False)
            bot.register_next_step_handler(msg,self.process_name_step)

    def process_number_step(self, message):
        MsgJs.addToLstInJson(self.chat_id,message.message_id)

        if (message.content_type == 'text'):
            if (message.text == '/start') or (message.text == '/חדש'):
                # time.sleep(0.01)
                self.next_step_reg(self.chat_id)

            elif self.check_phone(message.text):

                self.cli.phone = message.text
                msg = send_msg(self.chat_id,"מה המייל שלך? \n אם את/ה לא מעוניין/ת לרשום את המייל, יש לרשום \"דלג\" ללא המרכאות",delete=False)
                bot.register_next_step_handler(msg,self.process_email_step)
            else:
                msg = send_msg(self.chat_id,"יש לרשום מספר טלפון נייד בעל 10 ספרות וללא אותיות ו/או סימנים. לדוגמה - 0541231231 ,\n רשמו את המס' פלאפון שלכם",delete=False)
                bot.register_next_step_handler(msg,self.process_number_step)
        else:
            msg = send_msg(self.chat_id,"אנא השתמשו בטקסט בלבד,\n רשמו את המס' פלאפון שלכם",delete=False)
            bot.register_next_step_handler(msg,self.process_number_step)

    def check_phone(self, phone):
        RE_phone = re.compile("^[0][5][0-9][0-9]{3}[0-9]{4}$")
        if RE_phone.match(phone):
            return True
        else:
            return False

    def process_email_step(self, message):
        try:
            MsgJs.addToLstInJson(self.chat_id,str(message.message_id))

            if (message.content_type == 'text'):
                email = message.text
                if email == '/start' or email == '/חדש':
                    # deleteByList(self.chat_id)
                    self.next_step_reg(self.chat_id)

                elif email == "דלג":
                    text = "*פרטיך כפי שהזנת אותם הם:*\n" \
                           "*שם מלא:* " + self.cli.cli_name + "\n" \
                                                         "*מספר טלפון:* " + self.cli.phone + "\n" \
                                                                                        "האם את/ה מאשר/ת כי אלו הפרטים הנכונים?"
                    send_msg(self.chat_id, text, reply_m=self.confirm_reg())


                elif self.check_email(email):
                    self.cli.email = email
                    text = "*פרטיך כפי שהזנת אותם הם:*\n" \
                           "*שם מלא:* " + self.cli.cli_name + "\n" \
                                                         "*מספר טלפון:* " + self.cli.phone + "\n" \
                                                                                        "*מייל:* " + email + "\n" \
                                                                                                             "האם את/ה מאשר/ת כי אלו הפרטים הנכונים?"
                    send_msg(self.chat_id, text, reply_m=self.confirm_reg())

                else:
                    msg = send_msg(self.chat_id, "אנא ודא/י שהמייל שהכנסת הינו תקין, נסה/י שוב", delete=False)
                    bot.register_next_step_handler(msg,self.process_email_step)
            else:
                msg = send_msg(self.chat_id, "אנא השתמשו בטקסט בלבד,\n רשמו את המייל שלכם, או 'דלג' ללא מרכאות", delete=False)
                bot.register_next_step_handler(msg, self.process_email_step)

        except Exception as e:
            # bot.reply_to(message, print(e))
            log.Warn(self.chat_id)
            pass

    def check_email(self, email):
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if re.search(regex,email):
            return True
        else:
            return False

    def confirm_reg(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(btn("כן", ['Registration', 'conf_reg']))
        markup.add(btn("לא - חזרה לתהליך הרשמה", ['Registration', 'restart']))
        return markup

    def conf_reg(self):
        try:
            DB.insert("userdetails", 'user_id, customer_name, phone_number, email', f"'{self.chat_id}','{self.cli.cli_name}','{self.cli.phone}','{self.cli.email}'")
        except:
            log.Warn(self.chat_id) #BUG: mybe not needed

        txt = f"{self.cli.cli_name}"+" נרשמ/ה לבוט!"
        bot.send_message(SetJs.get("Channels")["update"], txt)
        send_msg(self.chat_id, endOFReg + '\n' + start_text(self.chat_id), mainKeyboard(self.chat_id))

    def restart(self):
        self.next_step_reg(self.chat_id)

