from CoreFuncs.func import *
import pandas as pd
class Admin:

    def __init__(self, call):

        self.call = call
        self.chat_id = str(call.from_user.id)
        method_name = AST(call)[2]
        method = getattr(self, method_name, lambda: 'Invalid')
        method()

    @staticmethod
    def hacky_init(call):
        Admin(call)

    ''' ['Admin', 'function', value] '''

    @staticmethod
    def textShowAppContact(message):
        chat_id = str(message.chat.id)
        MsgJs.addToLstInJson(chat_id, message.message_id)
        if (message.text == '/start') or (message.text == '/חדש'):
            mainMenu_msg(chat_id)
        else:
            customerName = message.contact.first_name
            customer_phone = phone_Refactor(message.contact.phone_number)
            customer_chatid = DB.getOneVal("userdetails","user_id",f"phone_number={customer_phone}")
            if customer_chatid is None:#if the customer isnt registered
                check_if_exist(chat_id)  # check if the appoints are stil in the calendar
                customer_chatid = "1"
            else:
                check_if_exist(chat_id)  # check if the appoints are stil in the calendar
                check_if_exist(customer_chatid)  # check if the appoints are stil in the calendar

            cli_appos = DB.get("Appointments", "appoint_id, service_name, date, time",f"user_id='{customer_chatid}'")
            admin_appos = DB.get("Admin_appoints", "appoint_id, service_name, date, time",f"cli_phone='{customer_phone}'")

            result = pd.concat([cli_appos, admin_appos])
            if result.empty:
                text = "ל"+customerName+" אין תורים עתידיים."
            else:
                text = "תורים עתידיים של " + customerName + ": \n\n"
                for i, row in result.iterrows():
                    text +="תור ל" + row["service_name"] + '-\n' + goodloking_date(row["date"]) + ', ' + row["time"][:5] + "\n\n"
                text += ' כל השעות ע"פ שעון 24 שעות.'

            deleteByList(chat_id)
            MsgJs.addToLstInJson(chat_id, bot.send_message(chat_id, text, reply_markup=onlyToMainKeyboard(), parse_mode='Markdown',
                             disable_web_page_preview=True).message_id)

    @staticmethod
    def textShowAppAdmin(chat_id):
            check_if_exist(chat_id)  # check if the appoints are still in the calendar
            result = DB.get('Admin_appoints')
            text = " "
            if result.empty:
                text += "לא קיימים תורים עתידיים שנקבעו על ידיך \n"
            else:
                text += "\nנא בחר/י תור לביטול:"
            return text

    @staticmethod
    def AdminCancelAPPKeyboard():
        try:
            appoints = DB.get("Admin_appoints",order="date, time")
            markup = types.InlineKeyboardMarkup()

            for i, ap in appoints.iterrows():
                text = ap["cli_name"] + ": " + ap["service_name"] + ',' + goodloking_date(ap["date"]) + ' , ' + ap[
                                                                                                                    "time"][
                                                                                                                :5]
                markup.add(btn(text, ['DelAppo', 'confKb', str(ap["appoint_id"])]))
        except:
            pass

        markup.add(btn(Home=True))
        return markup

    def select_del_appo(self):
        text = "האם את/ה בטוח שאתה רוצה לבטל את התור?"
        create_menu(self.call, text, confirmDelKeyboard(self.value))

    @staticmethod

    def confirmSendBroadMsg(message):
        chat_id = str(message.chat.id)
        MsgJs.addToLstInJson(chat_id, message.message_id)
        if message.text == '/start':
            send_msg(chat_id, start_text(chat_id), mainKeyboard(chat_id))
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(btn('כן', ['Admin', 'send_broad_msg', None]))
            markup.add(btn('שינוי הודעה', ['Admin', 'change_msg', None]))
            markup.add(btn(Home=True))
            BroadMessage[chat_id] = message.text
            send_msg(chat_id, "*ההודעה שהתקבלה היא:*\n" + message.text + "\n האם לשלוח את ההודעה לכלל הלקוחות?", reply_m = markup)


    def send_broad_msg(self):
        log.Choice(self.chat_id, "confirmed send broad message")
        self.sendBroadMsg()
        send_msg(self.chat_id, "ההודעה נשלחה בהצלחה!\n" + start_text(self.chat_id), mainKeyboard(self.chat_id))


    def change_msg(self):
        send_msg(self.chat_id, "*ההודעה הקודמת:*")
        send_msg(self.chat_id, BroadMessage[self.chat_id], delete=False)
        msg = send_msg(self.chat_id, "נא שלח/י את הודעת התפוצה,\n לחזרה לתפריט הראשי לחץ/י /start", delete=False)
        bot.register_next_step_handler(msg, Admin.confirmSendBroadMsg)

    def sendBroadMsg(self):
        bot.send_message(SetJs.get("Channels")["broad_msg"], BroadMessage[self.chat_id])
        clients = DB.get("userdetails")
        for i, cli in clients.iterrows():
            if self.chat_id != cli["user_id"]:
                bot.send_message(cli["user_id"], BroadMessage[self.chat_id],
                                 reply_markup=self.toDeleteKeyboard())  # its ok that the message wasnt saved

    def toDeleteKeyboard(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(btn("אישור", ['broad_msg'], Ver=False))
        return markup

    @staticmethod

    def chanelsKeyboard():
        markup = types.InlineKeyboardMarkup()
        markup.add(btn("🔹 לערוץ העדכונים 📌",link="joinchat/AAAAAFY4QUBW5t80hiiHEg"))
        markup.add(btn("🔹 לערוץ ההודעות ✉️",link="joinchat/AAAAAEwLLrdnXBfqXMAzfA"))
        markup.add(btn("🔹תמיכה 🔧",link='MegaKush'))
        markup.add(btn(Home=True))
        return markup

class Admin_Stock:
    ''' ['Admin_Stock', 'function'] '''
    def __init__(self,call):
        self.call = call
        self.chat_id = str(call.from_user.id)
        method_name = AST(call)[2]
        method = getattr(self, method_name, lambda: 'Invalid')
        method()

    @staticmethod
    def hacky_init(call):
        Admin_Stock(call)

    @staticmethod
    def text():
        services = DB.get('services')
        if services.empty:
            return False
        text = ''
        for i, s in services.iterrows():
            text += s['service_name'] + ' - ' + str(s['duration']) + ' - ' + str(s['price']) + '\n'
        return text

    @staticmethod
    def Keyboard():
        markup = types.InlineKeyboardMarkup()
        markup.add(btn("שינוי רשימת השירותים", ['Admin_Stock', 'ChangeStock']))
        markup.add(btn("חזרה לתפריט הראשי 🏠", ['Admin_Stock', 'home']))
        return markup

    @staticmethod
    def print_stock(format_txt):
        text = ''
        format_txt = format_txt.splitlines()
        for row in format_txt:
            details = row.split('-')
            name = details[0]
            duration = details[1].strip()
            price = details[2].strip()
            text += 'שם השירות - *' + name + '*\n'
            text += 'זמן התור' + ' - *' + duration + " דק'*\n"
            text += 'מחיר' + ' - *' + '₪' + price + '*'
            text += "\n🔸\n"
        return text


    def home(self):
        deleteByList(self.chat_id)
        MsgJs.addToLstInJson(self.chat_id, bot.send_message(self.chat_id,start_text(self.chat_id),
                                                      reply_markup=mainKeyboard(self.chat_id),
                                                      parse_mode='Markdown',
                                                      disable_web_page_preview=True).message_id)

    def ChangeStock(self):
        text = 'קידוד השירותים בפורמט -\n'
        text += "`שם השירות - זמן התור - מחיר `" + '\n\n'
        text += 'קידוד שירותים בפורמט באנגלית- (אותו דבר רק מראה)\n'
        text += "`service name - duration - Price`" + '\n\n'
        MsgJs.addToLstInJson(self.chat_id, bot.edit_message_text(chat_id=self.chat_id,
                                                                text=text,
                                                                message_id=self.call.message.message_id,
                                                                parse_mode='Markdown',
                                                                disable_web_page_preview=True).message_id)
        stock_txt = self.text()
        if not stock_txt:
            stock_txt ="שם השירות - זמן התור - מחיר\n" \
                  "שם השירות - זמן התור - מחיר\n"

        send_msg(self.chat_id, stock_txt, delete=False)
        msg = send_msg(self.chat_id,
                               "יש לשלוח מלאי חדש על פי הפורמט,\n ניתן להשתמש בהודעה לעיל 👆 ולשנות על פי הצורך.\n לחזרה לתפריט הראשי -> /start",delete=False)
        bot.register_next_step_handler(msg, self.proccess_ChangeStock)



    def proccess_ChangeStock(self, message):
        StockChange[self.chat_id] = message
        MsgJs.addToLstInJson(self.chat_id, str(message.message_id))

        try:
            # lines = message.text.splitlines()
            text = '*פרטי השירותים שהתקבלו:*\n\n'
            text += self.print_stock(message.text)
            text += 'האם ברצונך לעדכן את המלאי ?'
            send_msg(self.chat_id, text, self.ConfirmStockKeyboard())

        except:
            if (message.text == '/start'):
                txt = start_text(self.chat_id)
                deleteByList(self.chat_id)
                MsgJs.addToLstInJson(self.chat_id, bot.send_message(chat_id=self.chat_id,
                                                              text=txt,
                                                              reply_markup=mainKeyboard(self.chat_id),
                                                              parse_mode='Markdown',
                                                              disable_web_page_preview=True).message_id)
            else:
                msg = bot.send_message(self.chat_id, "מלאי לא תקין, אנא נסה שוב או לחץ על /start לביטול")
                MsgJs.addToLstInJson(self.chat_id, msg.message_id)
                bot.register_next_step_handler(msg, self.proccess_ChangeStock)

    def ConfirmStockKeyboard(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(btn("אשר שינוי + עדכן גירסה לבוט", ['Admin_Stock', 'changeStockConfirmed']))
        markup.add(btn("שינוי פרטי השירותים", ['Admin_Stock', 'change_msg']))
        markup.add(btn(Home=True))
        return markup

    def change_msg(self):
        send_msg(self.chat_id, "*ההודעה הקודמת:*")
        send_msg(self.chat_id, StockChange[self.chat_id].text, delete=False)
        msg = send_msg(self.chat_id, "יש לשלוח את השינויים הרצויים על פי הפורמט,\n ניתן להשתמש בהודעה לעיל 👆 ולשנות על פי הצורך.\n לחזרה לתפריט הראשי -> /start", delete=False)
        bot.register_next_step_handler(msg, self.proccess_ChangeStock)


    def changeStockConfirmed(self):
        lines = StockChange[self.chat_id].text.splitlines()
        DB.delete('services', 1)
        for row in lines:
            details = row.split('-')
            name = details[0]
            duration = details[1].strip()
            price = details[2].strip()
            DB.insert("services", 'service_id, service_name, duration, price', f"NULL,'{name}','{duration}','{price}'")

        changeVersion()
        create_menu(self.call, start_text(self.chat_id), mainKeyboard(self.chat_id),
                    string='השירותים עודכנו בהצלחה!')

