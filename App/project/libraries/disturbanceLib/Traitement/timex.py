import re
import datetime
import calendar



# Les cas qui posent probleme :

# "les lignes 12/35/26"
# ne repere pas les duree 



# Expression dates / moments de la journee
days = "(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)"
months = "(janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre)"
rel_day1 = "(aujourd'hui|demain)"
rel_day2 = "(soir|matin|apres-midi|service)"
dmy = "(mois|semaine)"
exp1 = "(debut|fin|milieu|ce|cette|toute)"
exp2 = "(prochain|prochaine)"
date = "("+"\d{1,2}"+"\/"+"\d{1,2}"+")"


# heures
h = "((" + "\d{1,2}" + "h" + "\d{1,2}" + ")|(" + "\d{1,2}" + "h" + "))" 


# intervales 
beg = "(depuis|du|entre le|le|les|des)"
end = "(jusqu'au|au|et le|et)"
h_beg = "(des|a partir de|a|de)"
h_end = "(jusqu'a|a)"


#  Expressions Regulieres
regexp1 = "(" + exp1 + "(( " + rel_day2 + "|" + dmy + ")|(" + " \S{2} " + rel_day2 + ")))" 
regexp2 = "((" + dmy + "|" + days + ") " + exp2 + ")"                        
regexp3 = "((" + days + " " + date + ")|(" + days + " \d{1,2} " + months + ")|(" + days + " \d{1,2}" + ")|(" + "\d{1,2} " + months + "))"

regexp4 = "((" +  h_beg + " " + h + " " + h_end + " " + h + ")|(" +  h_beg + " " + h + ")|(" + h + "))"

regexp = "(("  + date + "|" + regexp3 + "|" + "\d{1,2}" + ") " + end + " (" + date + "|" + regexp3 + "))" 
regexp5 = "((" + beg + " " + regexp + ")|(" + regexp + "))"


reg1 = re.compile(regexp1, re.IGNORECASE)  # ok
reg2 = re.compile(regexp2, re.IGNORECASE)  # ok
reg3 = re.compile(regexp3, re.IGNORECASE)  # ok
reg5 = re.compile(rel_day1, re.IGNORECASE) # ok
reg6 = re.compile(rel_day2, re.IGNORECASE) # ok
reg7 = re.compile(date)                    # ok

reg8 = re.compile(regexp4, re.IGNORECASE)
reg9 = re.compile(regexp5, re.IGNORECASE)

hashweekdays = {
    'LUNDI': 0,
    'MARDI': 1,
    'MERCREDI': 2,
    'jEUDI': 3,
    'VENDREDI': 4,
    'SAMEDI': 5,
    'DIMANCHE': 6}


hashmonths = {
    'JANVIER': 1,
    'FEVRIER': 2,
    'MARS': 3,
    'AVRIL': 4,
    'MAI': 5,
    'JUIN': 6,
    'JUILLET': 7,
    'AOUT': 8,
    'SEPTEMBRE': 9,
    'OCTOBRE': 10,
    'NOVEMBRE': 11,
    'DECEMBRE': 12}


class LastDayMonth(object):

    def __init__(self, year, month):
        self.month = month
        self.year = year
        self.day = 31
        self.Calcule()
 
    def Calcule(self):
        try:
            laDate = datetime.datetime(self.year, self.month, self.day)
        except:
            self.day = self.day - 1
            self.Calcule()
 
    def GetDay(self):
        return self.day
 


class ExtractTime(object):

    def __init__(self):
        self.times = []

                    
    def _clean_tag(self, tagged_text):
        
        tags = re.findall('<TIMEX>.*?</TIMEX>', tagged_text)
        for t in tags:
            if len(re.findall('<TIMEX>', t)) >= 2:
                tagged_text = re.sub(t, re.sub('</TIMEX>', '', t), tagged_text)

        return tagged_text


    def tag(self, text):
        """
           Tag les elements de text qui font reference a une date.
           Exemple :
           "Greve a la TBC le mardi 18 juin" 
           retourne "Greve a la TBC le <TIMEX>mardi 18 juin</TIMEX>" 
        """
        timex_found = []
        
        # "du 8 au 16/01"
        found = reg9.findall(text)
        found = [a[0] for a in found if len(a) > 1]
        for timex in found:
            timex_found.append(timex)

        # trouve les expressions du type "fin de soiree", "ce matin"
        found = reg1.findall(text)
        found = [a[0] for a in found if len(a) > 1]
        for timex in found:
            timex_found.append(timex)

        # "semaine prochaine"
        found = reg2.findall(text)
        found = [a[0] for a in found if len(a) > 1]
        for timex in found:
            timex_found.append(timex)

        # "vendredi 13"
        found = reg3.findall(text)
        found = [a[0] for a in found if len(a) > 1]
        for timex in found:
            timex_found.append(timex)

        # "demain"
        found = reg5.findall(text)
        for timex in found:
            timex_found.append(timex)

        # "dans la soiree"
        found = reg6.findall(text)
        for timex in found:
            timex_found.append(timex)
    
        # "26/10"
        found = reg7.findall(text)
        for timex in found:
            timex_found.append(timex)

        # "10h"
        found = reg8.findall(text)
        found = [a[0] for a in found if len(a) > 1]
        for timex in found:
            timex_found.append(timex)

        for timex in timex_found:
            text = re.sub(timex + '(?!</TIMEX>)', '<TIMEX>' + timex + '</TIMEX>', text)
                
        return self._clean_tag(text)


    def _make_list(self, date_start, date_end):
            
        list_date = []
            
        list_date.append(date_start)
        delta = date_end[0] - date_start[0]
        err = max(date_end[1],date_start[1])
        for d in range(0, delta.days):
            list_date.append([date_start[0].replace(day=date_start[0].day+d+1), err])

        return list_date


    def _split_inter(self, timex):
        s_bis = re.sub(r'\s' + end + r'\s',',', timex)
        s_ter = re.sub(beg + r'\s','', s_bis)
        return s_ter.split(',')
    

    def _set_err(self, err, d):
        d[1] = err
        return d


    def _set_time(self, hour, minute, d):
        d[0] = d[0].replace(hour=hour, minute=minute)
        return d


    def _apply_hour(self, hour, minute, l_date, err):
        l_date_tmp = map(lambda d:self._set_time(hour, minute, d), l_date) 
        return map(lambda d:self._set_err(err, d), l_date_tmp)


    def extract_time(self, tagged_text):
        """
           A partir d'un text retourne par la fonction tag, retourne les objets datetimes associes, 
           avec une erreur.
           Exemple :
           "<TIMEX>18 juin 2016</TIMEX>"
           retourne [datetime(2016, 6, 18), erreur]
           Cette erreur depend de l'expression concerne. Elle se compte en heure.
           Si il a plusieur element interprete comme une date dans le text, etract_time retourne une liste.
        """
        time_found = []

        #trouver tout les tag TIMEX dans tagge_text
        timex_regex = re.compile(r'<TIMEX>.*?</TIMEX>', re.DOTALL)
        timex_found = timex_regex.findall(tagged_text)
        
        timex_found = map(lambda timex:re.sub(r'</?TIMEX.*?>', '', timex), timex_found)
        

        if len(timex_found) == 1:
            if reg9.match(timex_found[0]):
                token = self._split_inter(timex_found[0])
                t1 = self.to_datetime(token[0])[0]
                t2 = self.to_datetime(token[1])[0]
                t1[0] = t1[0].replace(month=t2[0].month)
                if re.search(' ' + r'et le|et' + ' ', timex_found[0]):
                    time_found.append(t1)
                    time_found.append(t2)
                else:
                    time_found = self._make_list(t1, t2)
                return time_found
            else:
                return self.to_datetime(timex_found[0])

        elif len(timex_found) >= 2:
            if reg9.match(timex_found[1]):
                s_tag = '<TIMEX>' + timex_found[1] + '</TIMEX>'
                time_found = self.extract_time(s_tag)
                t_time = self.to_datetime(timex_found[0])[0]
                hour = t_time[0].hour
                minute = t_time[0].minute
                return self._apply_hour(hour, minute, time_found, t_time[1])

            elif (reg8.match(timex_found[1]) or reg1.match(timex_found[1]) or reg6.match(timex_found[1])) and reg9.match(timex_found[0]):
                s_tag = '<TIMEX>' + timex_found[1] + '</TIMEX> ' + '<TIMEX>' + timex_found[0] + '</TIMEX>'
                return self.extract_time(s_tag)

            else:
                d = datetime.datetime(2000, 1, 1).now()
                error = 10
                for i in range(0, len(timex_found)):
                    tmp_d = self.to_datetime(timex_found[i], d)[0]
                    if tmp_d[1] <= error or tmp_d[1] == 10:
                        d = tmp_d[0]
                        if tmp_d[1] != 10:
                            error = tmp_d[1]

                time_found.append([d, error])
                return time_found
        else:
            return []


    def to_datetime(self, timex, d=datetime.datetime(2000, 1, 1).now()):
        """
           A partir d'un Timex ( i.e <TIMEX>timex</TIMEX>) retourne le datetime associe.
        """
        date_found = []
        datetime_found = []

            
        #recupere la date d'aujourd'hui
        date = d

        datetime_found.append([date, 0])

        year = date.year
        month = date.month
        day = date.day
        hour = date.hour
        minute = date.minute

        error = 10

        timex = timex.lower()

        # "ce soir", "en fin de soiree", ...
        if re.match(exp1, timex):
            token = timex.split()
            if len(token) == 3:
                token.remove(token[1])
                
            if token[1] == 'soir':
                tmp_time = ['20.0', '21.30', '23.0']
            elif token[1] == 'matin':
                tmp_time = ['7.0', '9.30', '11.0']
            elif token[1] == 'apres-midi':
                tmp_time = ['13.0', '15.0', '18.0']
            elif token[1] == 'service':
                tmp_time = ['', '', '1.0']
                lastday = LastDayMonth(year, month).GetDay()
                day = (day + 1) % lastday
                if day == 1:
                    month = (month + 1) % 12
            
            if token[0] == 'debut':
                hour = int(tmp_time[0].split('.')[0])
                minute = int(tmp_time[0].split('.')[1])
                error = 1
                    
            elif token[0] in ['milieu', 'ce', 'cette']:
                hour = int(tmp_time[1].split('.')[0])
                minute = int(tmp_time[1].split('.')[1])
                if token[0] == 'milieu':
                    error = 1
                else:
                    error = 3
                
            elif token[0] == 'fin':
                hour = int(tmp_time[2].split('.')[0])
                minute = int(tmp_time[2].split('.')[1])
                error = 1
                    
            
        # "semaine prochaine", ...
        elif re.search(exp2, timex):
            if re.match(days, timex):
                today = date.weekday()
                lastday = LastDayMonth(year, month).GetDay()
                day = (day + 7 - today + 1 + hashweekdays[timex.split()[0]]) % lastday
                if day == 1:
                    month = (month + 1) % 12
                    
            elif re.match(dmy, timex):
                if timex.split()[0] == 'mois':
                    if month == 12:
                        year += 1
                        month = (month + 1) % 12
                        day = 1
                        
                elif timex.split()[0] == 'semaine':
                    today = date.weekday()
                    day += 7 - today
                    
        # "lundi 3/01"
        elif re.match(days, timex) and re.search(r'\d{1,2}' + r'\S' + r'\d{1,2}', timex):
            m = re.search(r'\d{1,2}' + r'\S' + r'\d{1,2}', timex)
            return self.to_datetime(m.group())


        # "lundi 3 janvier"
        elif re.match(days, timex) and len(timex.split()) == 3: 
            token = timex.split()
            day = int(token[1])
            month = hashmonths[token[2].upper()]
          
        # "samedi 18"
        elif re.match(days, timex) and len(timex.split()) == 2:
            token = timex.split()
            day = int(token[1])

        # "4 mars"
        elif re.match(r'\d{1,2}', timex) and len(timex.split()) == 2:
            token = timex.split()
            day = int(token[0])
            month = hashmonths[token[1].upper()]
                      
        # "demain"
        elif re.match(rel_day1, timex):
            if timex == 'demain':
                lastday = LastDayMonth(year, month).GetDay()
                day = (day + 1) % lastday
                if day == 1:
                    month = (month + 1) % 12
                # debut du servise
                hour = 5
                minute = 30
                

        # "dans la matinee"
        elif re.match(rel_day2, timex):
            if timex == 'soir':
                hour = 21
                error = 2
            elif timex == 'matin':
                hour = 9
                error = 3
            elif timex == 'apres-midi':
                hour = 16
                minute = 3
                error = 3


        # si timex est au format "DD/MM" ou "DD/MM/YYYY"
        elif re.match(r'\d{1,2}' + r'\/' + r'\d{1,2}', timex):
            f = re.findall(r'\d{1,4}', timex)
            day = int(f[0])
            month = int(f[1])
            # debut du servise
            hour = 5
            minute = 30

        # "11h", "9h30"
        elif reg8.match(timex):
            if re.match(h_beg, timex):
                timex = re.sub(h_beg, '', timex)
            
            token = timex.split('h')
            try:
                token.remove('')
                hour = int(token[0])
                minute = 0
                error = 0
            except:
                hour = int(token[0])
                minute = int(token[1])
                error = 0


        # "le 8" le mois choisie dans ce cas est le mois en cours.
        elif re.match(r'\d{1,2}', timex):
            day = int(re.findall(r'\d{1,2}', timex)[0])
            # debut du servise
            hour = 5
            minute = 30
            


        d = datetime.datetime(year, month, day, hour, minute)

        if d != date:
            datetime_found.append([d, error])

        if len(datetime_found) > 1:
            datetime_found.remove([date, 0])
        
        return datetime_found


        
