from settings import DB, GC, SetJs, bot
import traceback
from CoreFuncs.resources import log
from datetime import datetime, timedelta
from CoreFuncs.func import goodloking_date


class Client:
    def __init__(self, chat_id=None):
        self.chat_id = chat_id  # chat ID ?
        self.cli_name = None
        self.phone = None
        self.email = None

    # def userDetails(self, chat_id):
    def getUser(self,chat_id):
        user = DB.get('userdetails',where=f"user_id = {chat_id}")
        try:
            self.cli_name = user['customer_name'][0]
            self.phone = user['phone_number'][0]
            self.email = user['email'][0]
        except:
            log.Warn(chat_id,'note:Cant get details of user from db')
            # FinalEx(chat_id)

    def getUserByPhone(self, phone):
        user = DB.get('userdetails',where=f"phone_number = '{phone}'")
        if user.empty:
            return False
        else:
            try:
                self.cli_name = user['customer_name'][0]
                self.phone = user['phone_number'][0]
                self.email = user['email'][0]
            except:
                # f.Warn(chat_id,'note:Cant get details of user from db')
                # FinalEx(chat_id)
                pass
            return True

class Service:

    def __init__(self):
       self.serv_name = None
       self.dur = None
       self.price = None

    #

    def setServiceDetails(self,serv_id_lst):
        res = DB.get("services")
        res = res.loc[res["service_id"].isin(serv_id_lst)]
        try:
            self.serv_name = ', '.join(res["service_name"].tolist())
            self.dur = str(res['duration'].sum())
            self.price = res['price'].sum()
        except:
            log.Warn(txt='note:Cant get details of user from db')
            # FinalEx()

class Appoint(Client,Service):

    def __init__(self, chat_id = None):
       self.date = None
       self.time = None
       self.appo_id = None
       self.is_confirmed = None
       self.version = None
       # self.services = []
       Client.__init__(self, chat_id)
       Service.__init__(self)

    def setAppo(self,appo_id):
        #BUG: check if appo exists
        res = DB.get('Appointments', where=f"appoint_id='{appo_id}'")
        if not res.empty:
            self.chat_id = res['user_id'][0]  # only when not Admin
            self.getUser(self.chat_id)
            self.is_confirmed = res['is_confirmed'][0]
            self.version = res['version'][0]

        else:
            res = DB.get('Admin_appoints', where=f"appoint_id='{appo_id}'")
            if res.empty:
                return False
            else:
                self.cli_name = res['cli_name'][0]
                self.phone = res['cli_phone'][0]

        self.appo_id = res['appoint_id'][0]
        self.serv_name = res['service_name'][0]
        self.time = res['time'][0][:5]
        self.date = res['date'][0]
        return True

    def book_apoint(self, chat_id):
        try:

            whatsapp_link ="<a href='http://wa.me/972"+self.phone[1:]+"' id='ow459' __is_owner='true'>פתח שיחה בווצאפ</a>"
            summary = self.serv_name + " - " + self.cli_name
            description = "שיחה:\n" + self.phone + "\n\n"+whatsapp_link

            self.appo_id = self.book(summary,description)

            if (self.appo_id == -1):
                print('..')  # BAG: need to return error
            elif (self.appo_id == 0):

                return "במהלך הזמנתך התור נתפס, יש לבחור מועד אחר"
            else:
                self.addToDB(chat_id)
                if (self.email is not None) & (self.email != 'None'):
                    GC.addMail(self.appo_id,self.email)

                if chat_id in SetJs.get("Admins"):
                    text = '✅ נקבע תור ע"י ' + SetJs.get("Admins_name")[self.chat_id] + " ל" + self.cli_name + ":\n" + self.serv_name + ', ב-' + goodloking_date(self.date) + ' , ' + self.time[:5]
                    bot.send_message(SetJs.get("Channels")["update"], text)
                    return "\nהתור נקבע בהצלחה!\n"
                else:
                    text = '✅ נקבע תור ע"י ' +self.cli_name + ":\n" + self.serv_name+', ב-' + goodloking_date(self.date) + ' , ' + self.time[:5]
                    bot.send_message(SetJs.get("Channels")["update"], text)
                return "\nהתור נקבע בהצלחה !\nנא להגיע בזמן 🤗\n\n"

        except:
            print('Error while trying to book_apoint ')
            traceback.print_exc()
            return 'Error'

    def book(self, summary, description):

        start = (datetime.strptime(self.date + " " + self.time, '%Y-%m-%d %H:%M:%S'))
        start = datetime(start.year, start.month, start.day, start.hour, start.minute)
        end = start + timedelta(minutes=int(self.dur))
        isavil = self.last_check_avail(str(start), str(end))
        if isavil == True:
            start = start.isoformat()
            end = end.isoformat()
            event_result = GC.addAppo(start, end, summary, description )
            apointID = event_result['id']
            return apointID
        else:
            return 0

    def addToDB(self,chat_id):
        if str(chat_id) in SetJs.get('Admins'):
            try:
                DB.insert('Admin_appoints','cli_name, cli_phone, service_name, date, time, appoint_id',
                          f"'{self.cli_name}','{self.phone}','{self.serv_name}','{self.date}','{self.time}','{self.appo_id}'")
            except:
                log.Warn('Admin')

            cli_id = DB.getOneVal("userdetails","user_id",f"phone_number = '{self.phone}'")
            if cli_id:
                DB.insert('Appointments', 'user_id, service_name, appoint_id, date, time', f"'{cli_id}','{self.serv_name}','{self.appo_id}','{self.date}','{self.time}'")

        else:
            DB.insert('Appointments', 'user_id, service_name, appoint_id, date, time', f"'{chat_id}','{self.serv_name}','{self.appo_id}','{self.date}','{self.time}'")

    def last_check_avail(self,start,end):
        start = (datetime.strptime(start,'%Y-%m-%d %H:%M:%S')) - timedelta(hours=2)
        start = start.isoformat() + 'Z'

        end = (datetime.strptime(end,'%Y-%m-%d %H:%M:%S')) - timedelta(hours=2)
        end = end.isoformat() + 'Z'
        events_result = GC.getAppoList(start,end)
        events = events_result.get('items', [])

        if (events == []):
            return True
        else:
            return False

    def delAppo(self):
        try:
            GC.delAppo(self.appo_id)
            date = goodloking_date(self.date)

            try:
                DB.delete("Admin_appoints", f"appoint_id='{self.appo_id}'")
            except:
                pass

            try:
                DB.delete("Appointments", f"appoint_id='{self.appo_id}'")

            except:
                pass

            if str(self.chat_id) in SetJs.get('Admins'):
                txt = "התור התבטל בהצלחה,\n"
                update_txt = '❌ בוטל תור ע"י ' + SetJs.get("Admins_name")[self.chat_id] +" ל"+self.cli_name+ ":\n" + self.serv_name + ',' + goodloking_date(
                    self.date) + ' , ' + self.time[:5]
                bot.send_message(SetJs.get("Channels")["update"],update_txt)

            else:
                txt = "התור שלך ל" + self.serv_name + " "" בתאריך " + date + " בשעה " + self.time + " בוטל.\n נשמח לראותך שוב בפעם אחרת 😊\n\n"

                update_txt = '❌ בוטל תור ע"י ' + self.cli_name + ":\n" + self.serv_name + ',' + goodloking_date(self.date) + ' , ' + self.time[:5]
                bot.send_message(SetJs.get("Channels")["update"],update_txt)

            return txt
        except:
            traceback.print_exc()
            return "הביטול לא צלח , יש לפנות לבעל העסק"
            #return "הביטול לא צלח, יתכן כי התור כבר בוטל. "


