import subprocess
from subprocess import Popen
import os
import openpyxl
import threading
from constantes import constantes
from General import General
from PIL import Image, ImageTk
import math
import random
import time
from openpyxl.styles import Font,Alignment
from openpyxl_image_loader import SheetImageLoader
from openpyxl.cell import Cell
from openpyxl.styles.borders import Border, Side

#for Operations of Read and Write Over Documents
class documento:
     
     thread_object=None
     result=None
     estatus=0
     queue=[]
     ESTATUS_FREE=0
     ESTATUS_WORKING=1
     
     #Verify if the Thread is Finished each 1000 ms
     @classmethod
     def check(cls,root,thread):
         root.after(1000,cls.check_ifDone,root,thread)
      
     #Verify if the Thread is Finished and Execute the Required Operations 
     @classmethod
     def check_ifDone(cls,root,thread,comp=None):
     
        if(thread.is_alive()):
            cls.check(root,thread)
            return
        if(cls.result==None):
          cls.verify_queue()
          return
          
        from tiempo import tiempo
        from conexion_bd import conexion_bd
        from event_manager import Event_manager 
        if(type(cls.result).__name__=="list"):
            if(len(cls.result)<=0):
                cls.result=None
                cls.verify_queue()
                return
            from Process_Manager import Process_Manager
            if(cls.result[0]=="data formato"):
               #Read A Excel Format Data for Format Gestion Panel
               data=[]
               temp_dat=cls.result
               for i in range(0,len(temp_dat[2])):
                   data.append(temp_dat[2][i])
               if(data!=[]):
                  preview_dat=Process_Manager.get_data_process()
                  preview_dat["Formatos"]["Row_Requerid"]=cls.result[3][1]
                  Process_Manager.set_data_process(preview_dat)
                  Event_manager.set_comp_values(cls.result[1],data)                             
            elif(cls.result[0]=="modificar excel"):
                 #Modify a Format Data for Format Gestion Panel   
                 vent=Event_manager.vent
                 usr=Event_manager.user
                 Process_Manager.finish_update_formato(cls.result[1],usr,vent)               
 
        elif(cls.result==constantes.REQUEST_RESULT_GENERATE_DOCUMENT_WITH_MESSAGE):
             General.show_message("documentos generados","reportes creados")
        elif(cls.result==constantes.REQUEST_RESULT_DOWNLOAD_SUCCESS):
             General.show_message("documentos descargados exitosamente","Descarga Exitosa")
        elif(cls.result==constantes.REQUEST_RESULT_ERROR_NO_REFERENCE_EXCEL):
             General.show_error("error en no hay contenido de refernecia para escribir en el formato","Referencia Del formato Invalida")
        elif(cls.result==constantes.REQUEST_RESULT_ERROR_REFERENCE_EXCEL):
             General.show_error("error referencia no encontrada","Referencia Del Formato Invalida")
        elif(cls.result==constantes.REQUEST_RESULT_ERROR_ACCESS):
             General.show_error("error de acceso a la data,asegurese que el documento no esta abierto","Acceso Invalido")
        elif(cls.result==constantes.REQUEST_RESULT_ERROR_GET_DATA):
             General.show_error("error obteniendo recurso","error al encontrar recurso")
        elif(cls.result==constantes.REQUEST_RESULT_ERROR_FOUND_END_ROW):
             General.show_error("error imposible encontrar fila final del formato","Formato No Modificable")
        elif(cls.result==constantes.REQUEST_RESULT_ERROR_INVALID_CONTENT):
             General.show_error("error insuficiente contenido para escribir el documento","Contenido Invalido")
        cls.result=None
        
     #Verify if Exist a Request On Queue for Execute the Request
     @classmethod
     def verify_queue(cls):
       if(len(cls.queue)<=0):
          return
       dat_queue=cls.queue[0]
       temp=[]
       for i in range(1,len(cls.queue)):
           temp.append(cls.queue[i])
       cls.queue=[]
       cls.queue=temp
       cls.request(dat_queue[0],dat_queue[1],dat_queue[2],dat_queue[3])
        
     #Manage a Request for a Document
     @classmethod
     def request(cls,root,file_name,request_type,content=[None,None,None],open_file=False):
        if(cls.estatus!=cls.ESTATUS_FREE):
           cls.queue.append([root,file_name,request_type,content])  
           return 
        if(request_type==constantes.REQUEST_READ_EXCEL):
            cls.thread_object=threading.Thread(target=cls.read_excell,args=(file_name,content))
            cls.thread_object.start() 
            cls.check_ifDone(root,cls.thread_object)
        elif(request_type==constantes.REQUEST_MODIFIC_EXCEL):
            cls.thread_object=threading.Thread(target=cls.modif_excell,args=(file_name,content))
            cls.thread_object.start() 
            cls.check_ifDone(root,cls.thread_object)    
        elif(request_type==constantes.REQUEST_WRITE_EXCEL_FROM_EXISTENT_FORMAT):
            cls.thread_object=threading.Thread(target=cls.write_excell_from_formato,args=(file_name,content,open_file))
            cls.thread_object.start() 
            cls.check_ifDone(root,cls.thread_object)  
        elif(request_type==constantes.REQUEST_DOWNLOAD):
            cls.thread_object=threading.Thread(target=cls.download,args=(file_name,content[0],open_file))
            cls.thread_object.start() 
            cls.check_ifDone(root,cls.thread_object)
        elif(request_type==constantes. REQUEST_WRITE_NOTAS_CERTIFICADAS):
            cls.thread_object=threading.Thread(target=cls.write_notas_certific,args=(file_name,content))
            cls.thread_object.start() 
            cls.check_ifDone(root,cls.thread_object) 
        elif(request_type==constantes.REQUEST_WRITE_CRONOGRAM):
            cls.thread_object=threading.Thread(target=cls.write_cronograma,args=(file_name,content,open_file))                
            cls.thread_object.start() 
            cls.check_ifDone(root,cls.thread_object) 
        
   
     #Download a Document
     @classmethod 
     def download(cls,file_name,src,open_file):
        import requests    
        if(src==None or src==""):
           cls.result=constantes.REQUEST_RESULT_ERROR_GET_DATA
           return 
        cls.estatus=cls.ESTATUS_WORKING        
        response=requests.get(src)
        if(response.status_code>400):
           cls.estatus=cls.ESTATUS_FREE
           cls.result=constantes.REQUEST_RESULT_ERROR_GET_DATA
           return 
        data=response.content 
        file_name=file_name.replace("ñ","n")
        file_name=file_name.replace("Ñ","N")
        temp_file=open(file_name,"wb")
        temp_file.write(data)
        temp_file.close()
        if(open_file):
            #Open doc in Navigator
            os.startfile(file_name)
            cls.estatus=cls.ESTATUS_FREE
            cls.result=constantes.REQUEST_RESULT_OPERATION_SUCCEESS_NO_MESSAGE
        else:
           #Only Download
           cls.estatus=cls.ESTATUS_FREE
           cls.result=constantes.REQUEST_RESULT_DOWNLOAD_SUCCESS

     #Find the Last Row with Border On the Range RowStart-RowEnd of Document
     @classmethod
     def Find_EndRowStyle(cls,column_start,row_start,row_end,columns,pages):
         for i in range(column_start,len(columns)):
            col=columns[i]
            for row in range(row_start,row_end):
               cell_temp=pages[col+str(row)]  
               if((cell_temp.border.left.style is None and cell_temp.border.right.style is None )==False):
                   continue
               if((cell_temp.border.bottom.style is None and cell_temp.border.top.style is None)==False):
                  continue
               if(row-1>=0):               
                   return row-1
         return -1      
     
     #Set Cell Font for the Column Cell and the Border for the Cells Above of it
     @classmethod
     def set_cellStyle(cls,pages,cell,list_columns,row_index,index_column,end_row):
        cell.alignment=Alignment(horizontal="center")   
        borde=Border(left=Side(style='thin'),right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        cell.border=borde
        #Set Font of Column Cell
        if(index_column>=1):
           #not ColumnA
           col_prev=pages[list_columns[index_column-1]+row_index]
           if(col_prev!=None):
                if(col_prev.font!=None):
                   previous_font=pages[list_columns[index_column-1]+row_index].font
                   cell.font=Font(name=previous_font.name, size=previous_font.sz,bold=previous_font.b)                      
                else:
                  cell.font=Font(name="Calibri", size=11,bold=True)                      
        
        #Set Borders for the Cells Above 
        for k in range(int(row_index)+1,end_row+1):
            temp_cell=pages[list_columns[index_column]+str(k)] 
            temp_cell.alignment=Alignment(horizontal="center")   
            borde_t=Border(left=Side(style='thin'),right=Side(style='thin'),bottom=Side(style='thin'),top=Side(style='thin'))
            temp_cell.border=borde_t 
                   
     #Modify Columns of Excel File for Format Gestion Panel
     @classmethod          
     def modif_excell(cls,file_name,content):
        if(len(content)<4):
            General.show_error("Datos Recibidos Incompletos","Faltan Datos")
            return   
        values=content[0]
        reference=content[1]
        row_index=str(content[2])
        try:
          from io import BytesIO
          temp_file=BytesIO(file_name[0])         
          cls.estatus=cls.ESTATUS_WORKING
          excl= openpyxl.load_workbook(temp_file,data_only=True)
          pages= excl.active
          found_reference=False
          end_rowStyle=-1
          letter_index=-1
          columns=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
          end_col=len(columns)
          #get the reference data ( row and letter/column Index in document)
          for i in range(0,end_col):
              cell=pages[columns[i]+row_index]
              if(cell==None):
                 continue
              val=cell.value
              if(val!=None and val==reference):
                found_reference=True
                letter_index=i+1
                row_start=int(row_index)+1
                row_end=row_start+50
                end_rowStyle=cls.Find_EndRowStyle(i,row_start,row_end,columns,pages)
                break    
          if(found_reference==False):
              cls.estatus=cls.ESTATUS_FREE
              cls.result=constantes.REQUEST_RESULT_ERROR_REFERENCE_EXCEL
              return 
            
          num_campos=len(values)
          count=1
        
          for j in range(letter_index,end_col):
            if(count<num_campos):
                cell=pages[columns[j]+row_index] 
                if(cell==None):
                   continue 
                val=cell.value
                pages[columns[j]+row_index]=values[count]
                count+=1
                
                if(val==None or val=="" or val==" " and end_rowStyle!=-1):
                   cls.set_cellStyle(pages,cell,columns,row_index,j,end_rowStyle)
            else:
                #Remove border from cells irrelevants
                if(end_rowStyle<0):
                   continue
                initial=int(row_index)
                if(initial>1):
                    initial=initial-1
                for col in range(initial,end_rowStyle+1):
                    if(col>=int(row_index)):
                      pages[columns[j]+str(col)]=""
                      pages[columns[j]+str(col)].border=Border(left=Side(style=None),right=Side(style=None),bottom=Side(style=None),top=Side(style=None))
                    else:        
                      pages[columns[j]+str(col)].border=Border(left=Side(style=None),right=Side(style=None),bottom=Side(style=None),top=Side(style=None))          
          path_temp=constantes.FOLDER_DOCUMENTS+file_name[1]
          path_temp=path_temp.replace("Ñ","N")
          path_temp=path_temp.replace("ñ","n") 
          excl.save(path_temp) 
          excl.close()
          resultado=["modificar excel",path_temp]
          cls.estatus=cls.ESTATUS_FREE
          cls.result=resultado
        except:
            cls.estatus=cls.ESTATUS_FREE
            cls.result=constantes.REQUEST_RESULT_ERROR_ACCESS
            
          
     #Replace the The Indicated Notes in the required cells and show the document of 'Certified Notes' 
     @classmethod 
     def write_notas_certific(cls,file_name,content):

        if(len(content)<5):     
             cls.result=constantes.REQUEST_RESULT_ERROR_INVALID_CONTENT
             return            
        reference_cells=content[2]
        col_count=content[3]
        data_replace=content[4]
        num_replaces=len(content[4])
        message_on_End=content[5]
        if(len(reference_cells)<=0 or col_count<1):
             cls.result=constantes.REQUEST_RESULT_ERROR_NO_REFERENCE_EXCEL
             return              
        try:                         
            from io import BytesIO
            temp_file=BytesIO(file_name[1])         
            cls.estatus=cls.ESTATUS_WORKING
            excl_f = openpyxl.load_workbook(temp_file,data_only=True)
            pass_sheet="super password"
            pages_file = excl_f.active   
            pages_file.protection.sheet = True
            pages_file.protection.password =pass_sheet
            pages_file.protection.enable() 
            columns=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
            end_col=len(columns)
         
            #Read a Max of 40 Rows for Get the Reference Cells
            found=0
            reference_indexs=[] 
            row_limit=50
            #Replace cell Values with the Notes of Student            
            for i in range(1,row_limit):
               for j in range(0,end_col):             
                  cell=pages_file[columns[j]+str(i)]
                  if(cell==None):
                     continue
                  val=cell.value
                  if(val!=None  and num_replaces>0):
                          
                      for k in range(0,num_replaces):
                        #Replace Requerid Texts                     
                        if(val==data_replace[k][0]):
                            data_replace[k][1]=data_replace[k][1].upper()          
                            pages_file[columns[j]+str(i)]=val+" "+data_replace[k][1]
                      
                      #Get Reference Cells for Each Academic Year
                      if(found<5):
                        for k in range(0,len(reference_cells)):
                          if(val==reference_cells[k]):
                            temp_reference=[]
                            temp_reference.append(str(i+2))
                            temp_reference.append(columns[j])
                            temp_reference.append(columns[j+1])
                            temp_reference.append(val[0])
                            reference_indexs.append(temp_reference)
                            found=found+1
                            if(found>=5):
                               k=len(reference_cells)                           
            if(found<=0): 
               cls.estatus=cls.ESTATUS_FREE
               cls.result=constantes.REQUEST_RESULT_ERROR_REFERENCE_EXCEL
               return constantes.REQUEST_RESULT_ERROR_REFERENCE_EXCEL  
            
            #Set Califications values Using the Reference Cells
            for rf in range(0,len(reference_indexs)):
                refe_actual=reference_indexs[rf]
                row_count=content[0]
                row_init=0
                if(len(refe_actual)<=0):
                    #Reference Format Invalid
                    continue
                row_init=int(refe_actual[0])
                for dat in range(0,len(content[1])):
                  if(content[1][dat][0]!=refe_actual[3]):
                     continue
                  califs=content[1][dat]
                  for cal in range(1,len(califs)):
                     area=califs[cal][0]
                     nota=califs[cal][1]                           
                     cell_index=refe_actual[1]+str(row_init+(cal-1))     
                     pages_file[cell_index]=area.upper()
                     cell_index=refe_actual[2]+str(row_init+(cal-1))     
                     pages_file[cell_index]=nota.upper()    
            
            #Save the Document
            from openpyxl.workbook.protection import WorkbookProtection
            protect_pass='super-secret-password'
            excl_f.security=WorkbookProtection(workbookPassword = protect_pass, lockStructure = True)
            file_name[0]=file_name[0].replace("ñ","n")
            file_name[0]=file_name[0].replace("Ñ","N")
            excl_f.save(file_name[0])
            excl_f.close()      
            os.startfile(file_name[0])              
            cls.estatus=cls.ESTATUS_FREE
            cls.result=constantes.REQUEST_RESULT_OPERATION_SUCCEESS_NO_MESSAGE
        except:
             cls.estatus=cls.ESTATUS_FREE
             cls.result=constantes.REQUEST_RESULT_ERROR_ACCESS
             
      
     #Write a Excel Document from a Existent Format of Excel 
     @classmethod 
     def write_excell_from_formato(cls,file_name,content,open_file=False):
        
        if(len(content)<5):          
             cls.result=constantes.REQUEST_RESULT_ERROR_INVALID_CONTENT
             return          
        reference_cell=content[2]
        col_count=content[3]
        data_replace=content[4]
        num_replaces=len(content[4])
        message_on_End=content[5]
        if(reference_cell=="" or col_count==-1):
            cls.result=constantes.REQUEST_RESULT_ERROR_NO_REFERENCE_EXCEL
            return 
        try:     
            from io import BytesIO
            import requests
            pass_sheet="super password"
            temp_file=BytesIO(file_name[1])         
            cls.estatus=cls.ESTATUS_WORKING
            excl_f = openpyxl.load_workbook(temp_file,data_only=True)
            pages_file = excl_f.active   
            pages_file.protection.sheet = True
            pages_file.protection.password =pass_sheet
            pages_file.protection.enable()
            columns=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH']
            end_col=len(columns)
            found=False
            reference_indexs=[]
            requiere_reference=True
            if(len(content[1])<=0):
                requiere_reference=False
            limit_row=100
            #Read a Max of 100 Rows
            for i in range(1,limit_row):
               for j in range(0,end_col):
                  cell=pages_file[columns[j]+str(i)]
                  if(cell==None):
                     continue
                  val=cell.value
                  if(val==None or num_replaces<=0):
                     continue
                  
                  #Replace Content of Requerid Texts                  
                  for k in range(0,num_replaces):                    
                     if(val==data_replace[k][0]):
                         cls.replace_cell_of_format(val,data_replace[k][1],columns[j-1],columns[j],i,pages_file) 
                  
                  #Look for reference Cell
                  if(val==reference_cell and found==False and requiere_reference==True):
                       reference_indexs.append(str(i+1))
                       found=True
                       for k in range(0,col_count):
                         reference_indexs.append(columns[j+(1+k)])               
           
            if(requiere_reference==True):
               #require add data using reference Cell
               if(found==False):
                  cls.estatus=cls.ESTATUS_FREE
                  cls.result=constantes.REQUEST_RESULT_ERROR_REFERENCE_EXCEL
                  return   
               row_count=content[0]
               row_init=0
               if(reference_indexs!=[]):
                   row_init=int(reference_indexs[0])
               for row in range(0,row_count):
                 for col in range(0,col_count):
                    cell_index=reference_indexs[col+1]+str(row_init+row)
                    pages_file[cell_index]=content[1][row][col].upper()              
            
            #Write the Document
            file_name[0]=file_name[0].replace("ñ","n")
            file_name[0]=file_name[0].replace("Ñ","N")          
            from openpyxl.workbook.protection import WorkbookProtection
            protect_pass='super-secret-password'
            excl_f.security=WorkbookProtection(workbookPassword = protect_pass, lockStructure = True)  
            if(os.path.exists(file_name[0])):
               os.remove(file_name[0])
            excl_f.save(file_name[0])
            excl_f.close()           
            if(open_file): 
               os.startfile(file_name[0])              
            cls.estatus=cls.ESTATUS_FREE
            
            if(message_on_End):
               cls.result=constantes.REQUEST_RESULT_GENERATE_DOCUMENT_WITH_MESSAGE
            else:
               cls.result=constantes.REQUEST_RESULT_OPERATION_SUCCEESS_NO_MESSAGE
        except:            
             cls.estatus=cls.ESTATUS_FREE
             cls.result=constantes.REQUEST_RESULT_ERROR_ACCESS
            
     #replace value of a cell in a format When Write a Report from Excel Format
     @classmethod
     def replace_cell_of_format(cls,value_cell,value_replace,preview_column,column,index_row,page):
        from io import BytesIO
        import requests
        if(value_cell=="FOTO:"):
            page[column+str(index_row)]=""
            if(value_replace!="not found"):                                        
                try:
                    response=requests.get(value_replace)
                    if(response.status_code>=200 and response.status_code<400):
                        data_img=response.content
                        img = openpyxl.drawing.image.Image(BytesIO(data_img))
                        img.width=75
                        img.height=90
                        img.anchor = column+str(index_row-1)
                        page.add_image(img)
                    else:
                        page[column+str(index_row+1)]="FOTO"
                except:
                    page[column+str(index_row+1)]="FOTO"
            else:
                page[column+str(index_row+1)]="FOTO"
        else:
            valor=value_cell
            left_cell=False
            null_values=["NN","DIRECTOR","fecha_e","fecha_v","NOMBRES_C","CARGO_C","CEDULA_C","CEDULA_DIRE","Directivo","code","/"]
            left_cells_list=["copia de Cedula de Identidad","Copia de Partida de Nacimiento Original","partida de nacimiento Original","Boleta del periodos escolar anterior de ser neceario",
                        "Notas Cerificadas","Carta de Residencia","Copia de Cedula","2 Fotos","2 fotos del estudiante"]
            if(valor=="CEDULA_R:"):
                valor="CEDULA:"
            if(valor in null_values):
               valor=""
            elif(valor.startswith("Area N")==True):
                valor=""
            elif(valor=="CI dire"):
                valor="cedula: "
            elif(valor=="en el:"):
                valor="en el "
            elif(valor in left_cells_list):
                left_cell=True
            if(valor!="Aguas Calientes," and valor!="a los" and valor!="en el " and valor!="Correo del Representante:"):    
                value_replace=value_replace.upper()
            if(left_cell==True):
                page[preview_column+str(index_row)]=value_replace
            else:
                page[column+str(index_row)]=valor+" "+value_replace
      
      #write the data of Cronogram in  a Excel File      
     @classmethod 
     def write_cronograma(cls,file_name,content,open_file=False):
        if(len(content)<5):
             cls.result=constantes.REQUEST_RESULT_ERROR_INVALID_CONTENT
             return constantes.REQUEST_RESULT_ERROR_INVALID_CONTENT   
        reference_cell=content[2]
        col_count=content[3]
        data_replace=content[4]
        message_on_End=content[5]
        if(reference_cell=="" and col_count==-1):
            cls.result=constantes.REQUEST_RESULT_ERROR_NO_REFERENCE_EXCEL
            return 
        try:
            from io import BytesIO
            import requests
            temp_file=BytesIO(file_name[1])         
            cls.estatus=cls.ESTATUS_WORKING
            excl_f = openpyxl.load_workbook(temp_file,data_only=True) 
            num_pages=3
            for index_page in range(0,num_pages):
                 #Each Page of Cronogram
                 pages_file = excl_f.worksheets[index_page] 
                 pass_sheet="super password"  
                 pages_file.protection.sheet = True
                 pages_file.protection.password =pass_sheet
                 pages_file.protection.enable()                 
                 num_replaces=len(data_replace[index_page])
                 columns=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE','AF','AG','AH']
                 end_col=len(columns)
                 found=False
                 reference_indexs=[]
                 #Read a Max of 100 Rows
                 limit_row=50
                 
                 for i in range(1,limit_row):
                   for j in range(0,end_col):
                      #Inspect Each Cell on The Range of Row/Columns
                      cell=pages_file[columns[j]+str(i)]
                      if(cell==None):
                         continue
                      val=cell.value
                      if(val==None or num_replaces<=0):
                         continue 
                         
                      #Replace Cells Values                         
                      for k in range(0,num_replaces):
                          if(val!=data_replace[index_page][k][0]):
                             continue
                          valor=val
                          empty_vals=["xperiodox","NN","año_e","cierre_e"]
                          if(valor in empty_vals):
                               valor=""                                 
                          data_replace[index_page][k][1]=data_replace[index_page][k][1].upper()
                          pages_file[columns[j]+str(i)]=valor+" "+data_replace[index_page][k][1]
                     
                      #Add data from Reference Cells
                      if(val==reference_cell and found==False and content[1][index_page]!=[]):                             
                         reference_indexs.append(str(i+1))
                         for k in range(0,col_count):
                            reference_indexs.append(columns[j+(1+k)])
                         found=True
                         row_count=content[0][index_page]
                         row_init=0
                         row_init=i+1
                         for row in range(0,row_count):
                           for col in range(0,col_count):
                              cell_index=reference_indexs[col+1]+str(row_init+row)           
                              pages_file[cell_index]=content[1][index_page][row][col].upper()            
            from openpyxl.workbook.protection import WorkbookProtection
            protect_pass='super-secret-password'
            excl_f.security=WorkbookProtection(workbookPassword = protect_pass, lockStructure = True)
            excl_f.active=excl_f.worksheets[0]      
            file_name[0]=file_name[0].replace("ñ","n")
            file_name[0]=file_name[0].replace("Ñ","N")          
            excl_f.save(file_name[0])
            excl_f.close()                    
            
            if(open_file): 
               os.startfile(file_name[0])              
            cls.estatus=cls.ESTATUS_FREE
            if(message_on_End):
               cls.result=constantes.REQUEST_RESULT_GENERATE_DOCUMENT_WITH_MESSAGE
            else:
               cls.result=constantes.REQUEST_RESULT_OPERATION_SUCCEESS_NO_MESSAGE       
        except:            
             cls.estatus=cls.ESTATUS_FREE
             cls.result=constantes.REQUEST_RESULT_ERROR_ACCESS
             
          
         
     #Read a Excel File         
     @classmethod     
     def read_excell(cls,file_name,content):        
       try:
          from io import BytesIO
          temp_file=BytesIO(file_name)         
          cls.estatus=cls.ESTATUS_WORKING 
          excl = openpyxl.load_workbook(temp_file,data_only=True)
          pages = excl.active                          
          cols=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
          end_col=len(cols)
          row_end=50          
          destino=content[1]
          reference=content[2]          
          values=["data formato",destino]
          found=False
          index=[-1,-1]
          
          #Get Reference Cell
          for i in range(1,row_end):
             for j in range(0,end_col):              
                cell=pages[cols[j]+str(i)]
                if(cell==None):
                    continue
                val=cell.value
                if(val!=None and val==reference and found==False ):
                   found=True                  
                   index=[j,i] 
                   j=end_col                   
             if(found):
                break  
                
          if(found==False):
            cls.estatus=cls.ESTATUS_FREE
            cls.result=constantes.REQUEST_RESULT_ERROR_REFERENCE_EXCEL
           
          #Get Cell Values 
          values_cells=[]
          initial_index=""
          for row in range(index[0],end_col):
              cell_index=cols[row]+str(index[1])
              cell=pages[cell_index]
              if(initial_index==""):
                 initial_index=index[1]
              if(cell==None):
                continue
              val=cell.value
              if(val!=None ):
                  values_cells.append(str(val))
          values.append(values_cells) 
          values.append([reference,initial_index])            
          cls.estatus=cls.ESTATUS_FREE
          cls.result=values
       except:
           cls.estatus=cls.ESTATUS_FREE
           cls.result=constantes.REQUEST_RESULT_ERROR_ACCESS
           
     
    
     #Remove CSV File On temp Zips Folder When Read or Write the Zip File with CSV Files
     @classmethod 
     def clear_csv_zipFolder(cls,list_files):
         for name in list_files:
             if(name.endswith("readme.txt")):
                continue
             os.remove(name)
      
