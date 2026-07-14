import time
import datetime
import math

#Manage the Times and Dates
class tiempo:
   
    def __init__(self,ti_t=0):
	    self.time_type=ti_t
     
    #Return the diference of Years between actual data and Indicate Data     
    def get_diference_years(self,fecha):
        local=self.get_fecha().split("/")
        y1=int(local[2])
        fech=fecha.split("/")
        if(len(fech)==3):
          y2=int(fech[2])
          return str(abs(y1-y2))         
        return ""
     
    #Get the Estimated Date of Class Init 
    def get_inicio_clases(self):
        year=self.get_fecha().split("/")[2]
        mes="09"
        dia="16"
        days=["Mon","Tues","Wednes","Thurs","Fri","Satur","Sun"]
        d=datetime.datetime.strptime(dia+"-"+mes+"-"+year+" 00:00:00", "%d-%m-%Y %H:%M:%S")        
        res=days[d.weekday()]
        if(res=="Satur"):
             dia="18"
        elif(res=="Sun"):
             dia="17"
        return dia+"/"+mes+"/"+year
    
    #Return the Actual Date as a string in format D/M/Y  
    def get_fecha(self):
        local=time.localtime()
        res=time.strftime("%d/%m/20%y",local)
        return res
    
    #get the Age using a date of Reference
    def get_edad(self,fecha):
        fecha1=fecha.split("/")
        fecha2=self.get_fecha().split("/")
        years=0
        year1=int(fecha1[2])
        year2=int(fecha2[2])
        years=abs(year1-year2)
        mes1=int(fecha1[1])
        mes2=int(fecha2[1])
        dia1=int(fecha1[0])
        dia2=int(fecha1[0])
        if(mes2<mes1):
           years-=1
        elif(mes1==mes2 and dia2<dia1):
           years-=1  
        return years
    
    #get the next date  with a Offset using Minutes   
    def get_next_date3(self,fecha,hora,adicional_minutes=0):
    
        fech=fecha.split("/")
        hor=hora.split(":")
        if(len(fech)==3 and len(hor)==3):
           dia=int(fech[0])
           limit_day=31
           year=int(fech[2])
           mes=int(fech[1])
           hora_a=int(hor[0])
           min_a=int(hor[1])
           sec_a=int(hor[2])
           min_a+=adicional_minutes
           if(min_a>60):
              hora_a+=1
              min_a=min_a-60
           if(hora_a>=24):
              hora_a=0
              dia+=1 
           if(dia>limit_day):
              diferencia=dia-limit_day
              dia=diferencia
              mes+=1
              if(mes>12):
                 year+=1  
           str_mes=str(mes)
           str_dia=str(dia)
           if(mes<10):
               str_mes="0"+str(mes)  
           if(dia<10):
               str_dia="0"+str(dia)  
           new_date=[]
           new_date.append(str_dia+"/"+str_mes+"/"+str(year))
           new_date.append(str(hora_a)+":"+str(min_a)+":"+str(sec_a))           
           return new_date  
        else:
          return " "
    
    #get the next date  with a Offset using Years     
    def get_next_date4(self,fecha,adicional_years=0):
        fech=fecha.split("/")
        if(len(fech)==3 ):
           dia=int(fech[0])
           year=int(fech[2])
           mes=int(fech[1])
           year=year+adicional_years
           str_dia=str(dia)
           str_mes=str(mes)
           if(len(str_dia)<2):
              str_dia="0"+str_dia
           if(len(str_mes)<2):
              str_mes="0"+str_mes   
           return str_dia+"/"+str_mes +"/"+str(year)
        else:
           return ""
    
    #get the next date  with a Offset using Days   
    def get_next_date2(self,fecha,adicional_days=0):
    
        fech=fecha.split("/")
        if(len(fech)==3):
           dia=int(fech[0])
           limit_day=31
           year=int(fech[2])
           mes=int(fech[1])
           dia+=adicional_days
           if(dia>limit_day):
              diferencia=dia-limit_day
              dia=diferencia
              mes+=1
              if(mes>12):
                 year+=1  
           str_mes=str(mes)
           str_dia=str(dia)
           if(mes<10):
               str_mes="0"+str(mes)  
           if(dia<10):
               str_dia="0"+str(dia)           
           return str_dia+"/"+str_mes+"/"+str(year)
        else:
          return " "
       
    #get the next date  with a Offset using Months       
    def get_next_date(self,fecha,adicional_months=0):
        fech=fecha.split("/")
        if(len(fech)==3):
           year=int(fech[2])
           mes=int(fech[1])
           mes+=adicional_months
           if(mes>12):
             mes=mes-12
             year+=1
           return fech[0]+"/"+str(mes)+"/"+str(year)
        else:
          return " "
    
    #Convert a Number to String Value of a Month    
    def get_mes(self,numero):
       if(numero==1):
           return "Enero"
       elif(numero==2):
           return "Febrero"
       elif(numero==3):
           return "Marzo"
       elif(numero==4):
           return "Abril"
       elif(numero==5):
           return "Mayo"
       elif(numero==6):
           return "Junio"
       elif(numero==7):
           return "Julio"
       elif(numero==8):
           return "Agosto"
       elif(numero==9):
           return "Septiembre"
       elif(numero==10):
           return "Octubre"
       elif(numero==11):
           return "Noviembre"
       elif(numero==12):
           return "Diciembre"

    #get Full Date as a string (time and Date) with a offset of Minutes       
    def get_full_time(self,addicional_minutes=0):
    
        fecha=["",""]
        now = datetime.datetime.now()
        horas=now.hour    
        minutes=now.minute
        seconds=now.second
        dia=now.day
        mes=now.month
        año=now.year
        if(addicional_minutes==0):
           fecha[1]=str(horas)+":"+str(minutes)+":"+str(seconds)     
           fecha[0]=str(dia)+"/"+str(mes)+"/"+str(año) 
           return fecha  

        if((addicional_minutes%60)==0):
             horas+=int(addicional_minutes/60)
        else:
           resto=addicional_minutes%60
           horas+=int(addicional_minutes/60)
           minutes+=resto
           if(minutes>=60):
              resto=minutes%60
              minutes=int(resto)
              horas+=1   
        while(horas>=24):
            horas=horas-24
            dia+=1
            if(dia>=31):
               mes+=1
               dia=1
               if(mes>=12):
                  mes=1
                  año+=1
        fecha[1]=str(horas)+":"+str(minutes)+":"+str(seconds)     
        fecha[0]=str(dia)+"/"+str(mes)+"/"+str(año) 
        return fecha  

    #Get the time as a string with a offset in minutes in format H:M:S    
    def get_tiempo(self,addicional_minutes=0):
        now = datetime.datetime.now()
        horas=now.hour    
        minutes=now.minute
        seconds=now.second
        if(addicional_minutes==0):
           return str(horas)+":"+str(minutes)+":"+str(seconds)     
        if((addicional_minutes%60)==0):
             horas+=int(addicional_minutes/60)
        else:
           resto=addicional_minutes%60
           horas+=int(addicional_minutes/60)
           minutes+=resto
           if(minutes>=60):
              resto=minutes%60
              minutes=resto
              horas+=1
        if(horas>=24):
            horas=0 
        return str(horas)+":"+str(minutes)+":"+str(seconds)     
    
    #Return True if the first Hour is previuos to the Second Hour
    def is_previous_time(self,h1,h2,strict=True):
        
        hor1=h1.split(':')
        hor2=h2.split(':')
        if(len(hor1)<3 or len(hor2)<3):
            return False
        hora1=int( hor1[0])
        hora2=int( hor2[0])
        min1=int( hor1[1])
        min2=int( hor2[1])
        sec1=int( hor1[2])
        sec2=int( hor2[2])
        if(hora1<hora2):
           return True
        elif(hora1==hora2 and min1<min2):
           return True
        elif(hora1==hora2 and min1==min2 and sec1<sec2):
           return True  
        if(strict==False):
           if(hora1==hora2 and min1==min2 and sec1<=sec2):
               return True
               
        return False
    
    #Return True if the First date is previous to the second date    
    def is_previous(self,d1,d2,strict=True):
    
        date1=d1.split('/')
        date2=d2.split('/')
        if(len(date1)<3 or len(date2)<3):
            return False
        days1=int(date1[0])
        days2=int(date2[0])
        month1=int(date1[1])
        month2=int(date2[1])
        year1=int(date1[2])
        year2=int(date2[2])
        if(year1<year2):
           return True
        elif(year1==year2 and month1<month2):
           return True
        if(year1==year2 and month1==month2 and days1<days2):
           return True 
        if(strict==False):
          if(year1==year2 and month1==month2 and days1<=days2):
           return True
        return False    
	