from CoreFuncs.func import *
from datetime import datetime,timedelta
from CoreFuncs.classes import Appoint
from Files.text.Headers import ServsTexst, DatesText, TimingText
import time


class MakeAppo:
    """ ['MakeAppo', 'function', value] """
    def __init__(self,call):

        self.call = call
        self.chat_id = str(call.from_user.id)
        self.value = AST(self.call)[3]  # will break if not exists
        self.ap = AppList[self.chat_id]

        method_name = AST(call)[2]
        method = getattr(self, method_name, lambda: 'Invalid')
        method()


    @staticmethod
    def hacky_init(call):
        MakeAppo(call)



    @staticmethod
    def serviceKeyboard(chosen_servs = []):
        services = DB.get('services')
        markup = types.InlineKeyboardMarkup()
        for i,srv in services.iterrows():
            if str(srv["service_id"]) in chosen_servs:
                text = " ✅ " + str(srv["service_name"]) + "- ₪" + str(srv["price"]) + ""
                markup.add(btn(text,['MakeAppo','unselect_service',str(srv["service_id"])]))

            else:
                text = str(srv["service_name"]) + "- ₪" + str(srv["price"]) + ""
                markup.add(btn(text,['MakeAppo','select_service',str(srv["service_id"])]))

        markup.add(btn("הבא ⬅️",['MakeAppo','set_services',None]))
        markup.add(btn(Home=True))

        return markup

    def select_service(self):
        addToList(TempUsers,self.chat_id,self.value)
        create_menu(self.call,ServsTexst,self.serviceKeyboard(TempUsers[self.chat_id]))

    def unselect_service(self):
        TempUsers[self.chat_id].remove(self.value)
        create_menu(self.call,ServsTexst,self.serviceKeyboard(TempUsers[self.chat_id]))

    def set_services(self):
        if TempUsers[self.chat_id]: #if user chose services
            self.ap.setServiceDetails(TempUsers[self.chat_id])
            TempUsers.pop(self.chat_id)
            create_menu(self.call,DatesText,self.weekKeyboard(self.chat_id))

        else:
            txt = "*שים/י ❤ לא בחרת שירות רצוי,*\n"
            create_menu(self.call,txt+ServsTexst,self.serviceKeyboard(self.chat_id))

    def weekKeyboard(self,chat_id,in_use=False):
        var = int(datetime.now().strftime("%U"))
        # var = datetime.now().isocalendar()[1]
        if not in_use:
            TempUsers[chat_id] = var
        week = int(TempUsers[chat_id])
        markup = types.InlineKeyboardMarkup()
        lst = self.get_days_list()
        btns = []
        if (lst == []):
            text = "אין תורים פנויים בשבוע זה נא בחר באפשרות אחרת:"
            create_menu(chat_id,text,self.weekKeyboard(self.chat_id))  # BUG: check if work good
        else:
            count = 0
            for date in lst:
                btns.insert(0,btn(self.keyboard_date(str(date)),['MakeAppo','select_date',date]))
                count += 1
                if count == 3:
                    markup.add(*btns)
                    btns = []
                    count = 0
            if btns != []:
                markup.add(*btns)
                btns = []
            if week != var + SetJs.get("SchedualWeeksLimit"):
                btns.append(btn("שבוע הבא ◀️ ",['MakeAppo','next_week',None]))
            if week != var:
                btns.append(btn("▶️ שבוע קודם",['MakeAppo','last_week',None]))
            markup.add(*btns)
            # markup.add(types.InlineKeyboardButton(text="בתאריך אחר",callback_data="['" + Version + "','how_long','0']")), \
            # markup.add(
            #     types.InlineKeyboardButton(text="חזרה לתפריט הראשי 🏠",callback_data="['" + Version + "','Menu','0']"))
            markup.add(btn(Home=True))
        return markup

    def select_date(self):
        self.ap.date = self.value
        create_menu(self.call,TimingText + goodloking_date(self.ap.date),
                    self.timeKeyboard(self.chat_id,str(self.ap.date)))

    def next_week(self):
        TempUsers[self.chat_id] += 1
        create_menu(self.call,DatesText,self.weekKeyboard(self.chat_id,in_use=True))

    def last_week(self):
        TempUsers[self.chat_id] -= 1
        create_menu(self.call,DatesText,self.weekKeyboard(self.chat_id,in_use=True))

    def get_days_list(self):

        d = str(datetime.now().date().year) + "-W" + str(int(TempUsers[self.chat_id]) - 1)
        start_date = datetime.strptime(d + '-0',"%Y-W%W-%w").date()
        end_date = (start_date + timedelta(days=6))
        if start_date < datetime.now().date():
            start_date = datetime.now().date()
        temp_d = start_date
        lst = []
        while temp_d != end_date + timedelta(days=1):
            if (self.print_time(str(temp_d),self.chat_id) != []):
                lst.append(str(temp_d))
            temp_d = temp_d + timedelta(days=1)
        return lst

    def print_time(self,date,chat_id):  # MOVE to makeapp
        if (startTime(date) == None) or (endTime(date) == None):
            time_lst = []
        else:
            lst_av = self.check_available(str(date))  # list with start and end time of appoints
            time_lst = []
            now = datetime.now()
            nowminuts = now.time().minute
            if (nowminuts > 0):
                nowhour = (now + timedelta(hours=1)).time().hour
                now = now.replace(hour=nowhour,minute=0,second=0,microsecond=0)
            start_date = str(date) + " " + startTime(str(date))
            start_date = (datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S'))

            if (now.date() == start_date.date()) & (now.time() > start_date.time()):
                start_date = now + timedelta(hours=1)
            end_date = str(date) + " " + endTime(str(date))
            end_date = (datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S'))
            if lst_av == True:  # if all the day is available  print all the times
                temp = start_date
                service_dur = int(self.ap.dur)
                # service_dur = int(getDuration(AppList[chat_id][serv_index]))
                while temp < end_date:
                    time_lst.append(temp.time())
                    temp = temp + timedelta(minutes=service_dur)
            else:
                first_appo = (datetime.strptime((lst_av[0][0]),'%Y-%m-%d %H:%M:%S'))
                if (first_appo.time()) > (start_date.time()):
                    lst_new = [start_date,start_date]
                    lst_av.insert(0,lst_new)  # insert the start time
                lst_new = [end_date,end_date]
                lst_av.append(lst_new)  # insert the end time
                lst_size = len(lst_av)
                i = 0
                max_end = lst_av[0][1]
                max_end = (datetime.strptime(str(max_end),'%Y-%m-%d %H:%M:%S'))
                if max_end < now:
                    max_end = now + timedelta(hours=1)
                if max_end > end_date:
                    max_end = end_date
                while i + 1 < lst_size:
                    end_prev = lst_av[i][1]
                    end_prev = (datetime.strptime(str(end_prev),'%Y-%m-%d %H:%M:%S'))
                    if (max_end > end_prev):
                        end_prev = max_end
                    start_curr = lst_av[i + 1][0]
                    start_curr = (datetime.strptime(str(start_curr),'%Y-%m-%d %H:%M:%S'))
                    end_curr = (datetime.strptime(str(lst_av[i + 1][1]),'%Y-%m-%d %H:%M:%S'))
                    if (end_curr >= max_end) & (start_curr <= end_date):
                        if (end_curr >= end_date):
                            end_curr = end_date
                        free_time = self.free_app(str(start_curr),end_prev,self.chat_id)  # checks how many appoints can be
                        max_end = end_curr
                        if free_time > 0:
                            self.print_time_help(end_prev,free_time,time_lst,self.chat_id)
                    i += 1
        return time_lst

    def print_time_help(self,end_prev,free_count,lst,chat_id):
        # returns a list with the free time to schedual
        i = 1
        service_dur = int(AppList[self.chat_id].dur)
        end_prev = str(end_prev)[0:19]
        end_prev = (datetime.strptime(end_prev,'%Y-%m-%d %H:%M:%S'))
        lst.append(end_prev.time())
        while i < free_count:
            end_prev = (end_prev + timedelta(minutes=service_dur))
            lst.append(end_prev.time())
            i = i + 1

    def check_available(self,date):
        # if all day available return true, else return list with start and end time : [['2019-09-03 22:30:00', '2019-09-03 23:30:00']...]
        start = date + " " + startTime(date)
        start = (datetime.strptime(start,'%Y-%m-%d %H:%M:%S'))
        start = start - timedelta(hours=3)  # because of the 3 hours delay in the calendar
        start = start.isoformat() + 'Z'

        end = date + " " + endTime(date)
        end = (datetime.strptime(end,'%Y-%m-%d %H:%M:%S'))
        end = end.isoformat() + 'Z'
        events_result = GC.getAppoList(start,end)
        events = events_result.get('items',[])

        if not events:
            return True
        else:
            app_list = []
            for event in events:
                if event['start'].get('date',event['start'].get('date')) != None:  # if there is a all day event
                    start = startTime(date)
                    end = endTime(date)
                else:
                    start = event['start'].get('dateTime',event['start'].get('date'))
                    end = event['end'].get('dateTime',event['end'].get('date'))
                    if start[:10] != date:
                        start = startTime(date)
                    else:
                        start = self.find_time(start)[:8]
                    if end[:10] != date:
                        end = endTime(date)
                    else:
                        end = self.find_time(end)[:8]
                time_lst = [date + " " + start,date + " " + end]
                app_list.append(time_lst)
            return (app_list)

    def free_app(self,start_curr,end_prev,chat_id):
        duration = int(AppList[self.chat_id].dur)
        end_prev = str(end_prev)[0:19]
        start_curr = str(start_curr)[0:19]
        start_curr = (datetime.strptime(start_curr,'%Y-%m-%d %H:%M:%S'))
        end_prev = (datetime.strptime(end_prev,'%Y-%m-%d %H:%M:%S'))
        temp = end_prev + timedelta(minutes=duration)
        count = 0
        while temp <= start_curr:
            count += 1
            temp += timedelta(minutes=duration)
        return count

    def find_time(self,time):
        time_lst = time.split('T')[1].split('+')[0]  # takes only time
        return time_lst

    def keyboard_date(self,str_date):
        try:
            date = datetime.strptime(str_date,'%Y-%m-%d')
            day = date.weekday()
            txtday = datetime.strftime(date,"%d.%m.%y")[:5] + "-" + WeekDays[day]

            return txtday
        except:
            return 'Error'

    def timeKeyboard(self,chat_id,str_date=None,result=None):
        """Require or  str_date or result"""
        if result is None:
            result = self.print_time(str_date,chat_id)
            result = self.splitDateBut(result)
            TempUsers[chat_id] = [result,0]
        markup = types.InlineKeyboardMarkup()
        btns = []
        count = 0

        buttons = result[TempUsers[chat_id][1]]
        for i,date in enumerate(buttons):
            btns.insert(0,btn(str(date)[:5],['MakeAppo','select_time',str(date)]))
            count += 1
            if count == 3:
                markup.add(*btns)
                btns = []
                count = 0

        if btns != []:
            markup.add(*btns)
            btns = []

        if TempUsers[chat_id][1] + 1 != len(result):
            btns.append(btn("הבא ◀️ ",['MakeAppo','naxt_times',None]))
        if TempUsers[chat_id][1] != 0:
            btns.append(btn("▶️ הקודם",['MakeAppo','last_times',None]))
        markup.add(*btns)
        markup.add(btn("בחירת יום אחר ↪️",['MakeAppo','back_to_dates',None]))
        markup.add(btn(Home=True))
        return markup

    def select_time(self):
        AppList[self.chat_id].time = self.value
        text = " האם את/ה בטוח שאתה רוצה לקבוע תור ל" + self.ap.serv_name + "\nבתאריך " + goodloking_date(
            self.ap.date) + "\nלשעה " + self.ap.time[:5]
        create_menu(self.call,text,self.toconfirmKeyboard())

    def naxt_times(self):
        TempUsers[self.chat_id][1] += 1
        create_menu(self.call,TimingText + goodloking_date(self.ap.date),
                    self.timeKeyboard(self.chat_id,result=TempUsers[self.chat_id][0]))

    def last_times(self):
        TempUsers[self.chat_id][1] -= 1
        create_menu(self.call,TimingText + goodloking_date(self.ap.date),
                    self.timeKeyboard(self.chat_id,result=TempUsers[self.chat_id][0]))

    def back_to_dates(self):
        create_menu(self.call,DatesText,self.weekKeyboard(self.chat_id))

    def splitDateBut(self,lst):
        new_lst = []
        temp = []
        count = 0
        for date in lst:
            count += 1
            temp.append(date)
            if count == 5 * 3:
                new_lst.append(temp)
                temp = []
                count = 0

        if temp != []:
            new_lst.append(temp)

        return new_lst

    def toconfirmKeyboard(self):
        markup = types.InlineKeyboardMarkup()
        # if (not delete):
        markup.add(btn('כן',['MakeAppo', 'confirm_appo', None]))
        markup.add(btn('בחירת שעה אחרת', ['MakeAppo', 'back_to_time', None]))
        markup.add(btn('לא - חזרה לתפריט', ['MainMenu', '0', None]))

        # else:
        #     markup.add(btn('כן', ['All', 'MakeAppo', 'confirm_dell_appo', appo_indexer]))
        #     markup.add(btn('לא', ['All', 'MainMenu', '0', None]))
        return markup

    def confirm_appo(self):
        txt = self.ap.book_apoint(self.chat_id) + " " + start_text(self.chat_id)
        create_menu(self.call, str(txt), mainKeyboard(self.chat_id))

    def back_to_time(self):
        date = AppList[self.chat_id].date
        create_menu(self.call, TimingText, self.timeKeyboard(self.chat_id, str(date)))


class DelAppo:
    """ ['DelAppo', 'function', value] """

    def __init__(self,call):

        self.call = call
        self.chat_id = str(call.from_user.id)
        self.value = AST(self.call)[3]  # will break if not exists
        method_name = AST(call)[2]
        method = getattr(self,method_name,lambda: 'Invalid')
        method()

    @staticmethod
    def hacky_init(call):
        DelAppo(call)

    @staticmethod
    def cancelAPPKeyboard(chat_id):
        try:
            if str(chat_id) in SetJs.get('Admins'):
                appoints = DB.get("Admin_appoints",order="date, time")
            else:
                appoints = DB.get("Appointments",where=f"user_id={chat_id}",order="date, time")

            markup = types.InlineKeyboardMarkup()
            for i,ap in appoints.iterrows():
                if str(chat_id) in SetJs.get('Admins'):
                    text = ap["cli_name"] + ": "
                else:
                    text = " "
                text += ap["service_name"] + ' ב- ' + goodloking_date(ap["date"]) + ' ,' + ap["time"][:5]

                markup.add(btn(text,['DelAppo','confdel',str(ap["appoint_id"])]))


        except:
            pass
        markup.add(btn(Home=True))
            # markup.add(
            # types.InlineKeyboardButton(text="חזרה לתפריט הראשי 🏠",callback_data="['" + Version + "','Menu','0']"))
        return markup

    def confdel(self):
        text = "האם את/ה בטוח שאתה רוצה לבטל את התור?"
        if self.chat_id not in SetJs.get("Admins"):
            now = datetime.now()
            ap = GC.getAppo(self.value)
            time = datetime.strptime(ap["start"]["dateTime"][:19],'%Y-%m-%dT%H:%M:%S')
            if now > time - cancel_limit:
                text = "התור שהנך רוצה לבטל חורג מזמן הביטול האפשרי,\n יש ליצור קשר עם בעל העסק על מנת לבטל תור זה.\n\n " + start_text(
                    self.chat_id)
                create_menu(self.call,text,mainKeyboard(self.chat_id))
            else:
                create_menu(self.call,text,self.confKb())

        # time.sleep(1.5)
        # print(chat_id + f": stat ->{Stat[chat_id]}")
        else:
            create_menu(self.call,text,self.confKb())

    def confKb(self):
        markup = types.InlineKeyboardMarkup()
        markup.add(btn('כן', ['DelAppo', 'dell_appo', self.value]))
        markup.add(btn('לא', ['MainMenu', '0', None]))
        return markup

    def dell_appo(self):
        ap = Appoint()
        exist = ap.setAppo(self.value)
        if not exist:
            txt = "תור זה אינו זמין,\n הפעולה *לא* נקלטה במערכת.\n"+start_text(self.chat_id)
        else:
            if str(self.chat_id) in SetJs.get('Admins'):
                ap.chat_id = self.chat_id

            txt = ap.delAppo() + "\n" + start_text(self.chat_id)

        create_menu(self.call, str(txt), mainKeyboard(self.chat_id))

