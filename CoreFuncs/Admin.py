# from CoreFuncs.settings import *
from CoreFuncs.func import *

class Admin:

    def __init__(self,call):

        self.call = call
        self.chat_id = str(call.from_user.id)
        ActiveUsers.append(self.chat_id)
        self.value = AST(self.call)[4]  # will break if not exists
        self.ap = AppList[self.chat_id]
        method_name = AST(call)[3]
        method = getattr(self,method_name,lambda: 'Invalid')
        method()
        ActiveUsers.remove(self.chat_id)


    @staticmethod
    def hacky_init(call):
        Admin(call)

    ''' ['Admin', 'function', value] '''

    @staticmethod
    def textShowAppContact(chat_id, message):
        MsgJs.addToLstInJson(chat_id,message.message_id)
        if (message.text == '/start') or (message.text == '/חדש'):
            mainMenu_msg(chat_id)
        else:
            customerName = message.contact.first_name
            customer_phone = phone_Refactor(message.contact.phone_number)
            customer_chatid=DB.getOneVal("userdetails","user_id",f"phone_number={customer_phone}")
            if customer_chatid is None:#if the customer isnt registered
                check_if_exist(chat_id)  # check if the appoints are stil in the calendar
                customer_chatid="1"
            else:
                check_if_exist(chat_id)  # check if the appoints are stil in the calendar
                check_if_exist(customer_chatid)  # check if the appoints are stil in the calendar

            cli_appos = DB.get("Appointments","appoint_id, service_name, date, time",f"user_id='{customer_chatid}'")
            admin_appos = DB.get("Admin_appoints","appoint_id, service_name, date, time",f"cli_phone='{customer_phone}'")

            result = pd.concat([cli_appos,admin_appos])
            if result.empty:
                text = "ל"+customerName+" אין תורים עתידיים."
            else:
                text = "תורים עתידיים של " + customerName + ": \n\n"
                for i,row in result.iterrows():
                    text +="תור ל" +row["service_name"] + '-\n' + goodloking_date(row["date"]) + ', ' + row["time"][:5] + "\n\n"
                text += ' כל השעות ע"פ שעון 24 שעות.'

            deleteByList(chat_id)
            MsgJs.addToLstInJson(chat_id, bot.send_message(chat_id, text, reply_markup=onlyToMainKeyboard(), parse_mode='Markdown',
                             disable_web_page_preview=True).message_id)

    @staticmethod
    def textShowAppAdmin(chat_id):
        try:
            check_if_exist(chat_id)  # check if the appoints are still in the calendar
            result = DB.get('Admin_appoints')
            text = " "
            if result.empty:
                text += "לא קיימים תורים עתידיים שנקבעו על ידיך \n"
            else:
                text += "\nנא בחר/י תור לביטול:"
            return text
        except:
            log.Warn(chat_id)
            FinalEx(chat_id)

    @staticmethod
    def AdminCancelAPPKeyboard():
        try:
            appoints = DB.get("Admin_appoints",order="date, time")
            markup = types.InlineKeyboardMarkup()

            for i,ap in appoints.iterrows():
                text = ap["cli_name"] + ": " + ap["service_name"] + ',' + goodloking_date(ap["date"]) + ' , ' + ap[
                                                                                                                    "time"][
                                                                                                                :5]
                markup.add(btn(text,['DelAppo', 'confKb', str(ap["appoint_id"])]))
                # markup.add(
                #     types.InlineKeyboardButton(text=text,callback_data="['" + Version + "','delete','" + str(
                #         ap["appoint_id"]) + "']"))
        except:
            pass

        markup.add(btn(Home=True))
        return markup

    def select_del_appo(self):
        text = "האם את/ה בטוח שאתה רוצה לבטל את התור?"
        create_menu(self.call,text,confirmDelKeyboard(self.value))

