#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 11:06:18 2021

@author: tzework
"""
from Figs.figClass import TMMfigure,TMMfigurefull
from DB.optical_data_db import ODB_class
from TMM.TMM_class import ncohTMM
from extra.TMM_postprocess import PostProcess
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy import interpolate as ipl
import numpy as np
from PIL import Image, ImageTk
import os
import sys

class container():
    pass

class LoadData():
    def __init__(self):
        self.PJ_name='Project_name.proj'#has to be here
        self.root = tk.Tk()
        self.root.geometry("1000x680")
        self.root.title("TMM GUI APP")
        self.init_mainframe()
        self.init_choosedb()
        try:
            (self.dbdirectory,self.pjdirectory)=self.check_ini()
        except:
            self.dbdirectory='Documents'
            self.pjdirectory='Documents'
            self.write_to_ini()
            
    def check_ini(self):
        with open(os.path.join(os.path.dirname(__file__),'TMM_guiconfig.ini'), 'r') as f:
            for line in f:
                a=line.strip()
                tmp=a.split('=')
                if tmp[0]=='database_path':
                    dbdirectory=tmp[-1]
                if tmp[0]=='projectfile_path':
                    filedirectory=tmp[-1]
            return (dbdirectory,filedirectory)
            
    def write_to_ini(self):
        write=[]
        write.append('database_path='+self.dbdirectory)
        write.append('projectfile_path='+self.pjdirectory)
        with open(os.path.join(os.path.dirname(__file__),'TMM_guiconfig.ini'),'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')


    def init_lists_variables(self):
        self.range=tk.StringVar()
        self.pol_list=['s','average','p']
        self.angle = tk.DoubleVar()#taken also for the result window as wavelength
        self.angle.set(0)
        self.absorption_layer=tk.StringVar()#taken also for the result window as current
        self.column_button_span=3
        self.absorption_column=self.column_button_span+6
        self.button_column=1
        self.name_column=self.column_button_span+1
        self.material_column=self.column_button_span+2
        self.unit_column=self.column_button_span+4
        self.thick_column=self.column_button_span+3
        self.coh_column=self.column_button_span+5
        self.row_offset=0
        self.layer_name_list=["Input media", "Exit media"] #list of layer_name_list
        self.name_Menu=[]#list for storing tklabels where layer_name_list will be displayed
        self.layer_mat_list=[]#list for storing tkstring vars for reading out the material sequence we need variable for each layer so that they are independent materials
        self.material_Menu=[]#list for storing tkOption menus in which self.layer_mat_list is located materials
        self.coh_list=['coh', 'ncoh']
        self.layer_coh_list=[]#same as for the material option storing tkstring vars coh/ncoh
        self.coh_Menu=[]#for storing tkPtions menus coh/ncoh

        self.unit_list=['mm', 'μm' ,'nm']
        self.layer_unit_list=[]#same as for the material option storing tkstring vars coh/ncoh
        self.unit_Menu=[]#for storing tkPtions menus coh/ncoh

        self.layer_thick_list=[]
        self.thick_Menu=[]
        self.absorption_Menu=[]
        self.layer_counter=0
        #hardcoded
        self.step_list=[5., 10., 30. ,50.]
        self.angle_min=0
        self.angle_max=80
        self.angle_step=5
        #wavelengths simulation step
        self.step_counter=1
        self.step=tk.StringVar()#taken also  for the result list for polarization
        self.step.set(self.step_list[self.step_counter])

    #this is also used for saving project file            
    def Add_items(self,text,itemlist,sep):
        for item in itemlist:
            text=text+str(item)+sep
        return text[:-1]

    def init_start(self):
        self.root.mainloop()

    def Placeholder(self):
        pass

    def init_mainframe(self):
        self.mainframe = tk.Frame(self.root)
        self.mainframe.grid(column=0,row=0)
        self.mainframe.columnconfigure(0, weight = 1)
        self.mainframe.rowconfigure(0, weight = 1)
        self.mainframe.pack(pady = (0,50), padx = (25,25))
        self.error=tk.StringVar()
        self.errormsg=tk.StringVar()
        self.error.set('')
        self.errormsg.set('\n')
        self.elb=tk.Label(self.mainframe, textvariable=self.error, fg='#f00')
        self.elb.grid(row = 0, column = 4)
        self.emlb=tk.Label(self.mainframe, textvariable=self.errormsg, fg='#f00')
        self.emlb.grid(row = 0, column = 5)

    def init_sideframe(self):
        self.sideframe=tk.Frame(self.mainframe)
        self.sideframe.grid(column=self.button_column,row=self.row_offset+3,columnspan=self.column_button_span,rowspan=600)


    def init_choosedb(self):
        textlbl=tk.Label(self.mainframe, text="Open the data base with optical\ndata or load the project file.", borderwidth=2,relief=tk.GROOVE,bg='lightgray')
        textlbl.grid(row = 1, column = 4, columnspan=2)


        openDB=tk.Button(self.mainframe, text="Open DB", command=self.Get_DB,width=9,bg='lightgray')
        openDB.grid(row=2,column=4)
        tk.Button(self.mainframe, text="Open project", command=self.Load_project,width=9,bg='lightgray').grid(row=2,column=5)
    
    def Load_project(self):
        check=[]
        self.layerstructure=container()
        filename = askopenfilename(title="Select project file.", initialdir=self.pjdirectory, filetypes=[("Project files","*.proj")])
        self.error.set('')
        self.errormsg.set('\n')
        if filename:
            (self.pjdirectory,self.PJ_name)=os.path.split(filename)#to record where is the project directory
            with open(filename, 'r') as f:
                for line in f:
                    a=line.strip()#removes \n at the end
                    tmp=a.split('=')
                    if tmp[0]=='Database':
                        self.DB_name=tmp[-1]
                        check.append(1)
                    if tmp[0]=='Input_angle':
                        self.layerstructure.Thin=int(tmp[-1])
                        check.append(1)
                    if tmp[0]=='Absorption_layer':
                        self.layerstructure.absorption_layer=tmp[-1]
                        check.append(1)
                    if tmp[0]=='Simulation_range':
                        self.layerstructure.range=tmp[-1]
                        check.append(1)
                    if tmp[0]=='Simulation_step':
                        self.layerstructure.step=float(tmp[-1])
                        check.append(1)
                    if tmp[0]=='Layer_material':
                        self.layerstructure.layermaterial=tmp[-1].split(',')
                        check.append(1)
                    if tmp[0]=='Layer_name':
                        self.layerstructure.layernames=tmp[-1].split(',')
                        check.append(1)
                    if tmp[0]=='Layer_coherence':
                        self.layerstructure.layerprop=tmp[-1].split(',')
                        check.append(1)
                    if tmp[0]=='Layer_thickness_units':
                        self.layerstructure.units=tmp[-1].split(',')
                        check.append(1)
                    if tmp[0]=='Layer_thickness':
                        self.layerstructure.thickness=[]
                        for item in tmp[-1].split(','):
                            self.layerstructure.thickness.append(float(item))
                        check.append(1)
                if sum(check)!=10:
                    self.error.set('Error:')
                    self.errormsg.set('Project file\nis corrupted')
                else:
                    self.connect_check_DB()
                    if self.errorDB=='':
                        self.Get_available_materials_from_DB()
                        for item in self.layerstructure.layermaterial:
                            if item not in self.mat_list:
                                self.error.set('Error:')
                                self.errormsg.set('Project file\nis corrupted')
                        if self.error.get()=='':
                            self.write_to_ini()
                            self.init_mat_window()
                            self.Rebuild_structure()

        else:
            pass

    def Close(self):
        try:
            self.conn.close()
        except:
            pass
        self.root.destroy()
        sys.exit()
        
    def connect_check_DB(self):
        self.error.set('')
        self.errormsg.set('\n')
        self.conn,self.errorDB=ODB_class().make_connection(self.DB_name)
        if self.errorDB!='':
            self.error.set('Error:')
            self.errormsg.set(self.errorDB)
        else:
            self.errorDB=ODB_class().table_test(self.conn)
            if self.errorDB!='':
                self.error.set('Error:')
                self.errormsg.set(self.errorDB)


    def Get_DB(self):
        self.DB_name = askopenfilename(title="Select database.", initialdir=self.dbdirectory, filetypes=[("Database files","*.db *.db3 *.sqlite *.sqlite3")])
        if self.DB_name:
            self.dbdirectory=os.path.dirname(self.DB_name)
            self.connect_check_DB()
            if self.errorDB=='':
                self.write_to_ini()
                self.init_mat_window()
        else:
            pass

    def Get_available_materials_from_DB(self):
        data=ODB_class().get_materials(self.conn)
        self.mat_list=[]
        self.mat_id={}#dictionary so I use layername to find layer id
        self.wlength_unit={}
        self.wlength_min={}
        self.wlength_max={}
        for rows in data:
            string=rows[0]+':'+str(rows[1])+'-'+str(rows[2])+'('+rows[3]+')'+'['+str(rows[4])+']'
            self.mat_list.append(string)
            self.mat_id.update({string: rows[5]})#material ID from database
            self.wlength_unit.update({rows[5]: rows[3]})#wavelength units for materials
            self.wlength_min.update({rows[5]: round(self.convert_units(rows[1],rows[3]),11)})#round is needed to avoid showing grabage numerical errors
            self.wlength_max.update({rows[5]: round(self.convert_units(rows[2],rows[3]),11)})#round is needed to avoid showing grabage numerical errors

    def init_mat_window(self):
        self.error.set('')
        self.errormsg.set('\n')
        self.mainframe.destroy()
        self.init_mainframe()
        self.init_lists_variables()
        self.init_sideframe()
        self.Add_title_labels()
        self.Add_Buttons()
        self.Get_available_materials_from_DB()
        self.Add_layer() #input medium
        self.Add_layer() #exit medium
        self.Add_input_light()
        self.set_range(0)

    def Add_Buttons(self):
        dirname=os.path.dirname(__file__)#path of this __file__ not the __main__
        imagepath=os.path.join(dirname, 'images', "button.png")
        image = Image.open(imagepath)
        self.buttonleft=ImageTk.PhotoImage(image)
        self.buttonright=ImageTk.PhotoImage(image.rotate(180))

        tk.Button(self.sideframe, text="Open another\nproject", command=self.Load_project,bg='lightgray',width=10).grid(row=self.row_offset+4,column=self.button_column, columnspan=self.column_button_span)
        tk.Button(self.sideframe, text="Reset\nstructure", command=self.init_mat_window,bg='lightgray',width=10).grid(row=self.row_offset+2,column=self.button_column, columnspan=self.column_button_span)
        tk.Button(self.sideframe, text="Add layer", command=self.Add_layer,bg='lightblue',width=10).grid(row=self.row_offset+5,column=self.button_column, columnspan=self.column_button_span)
        tk.Button(self.sideframe, text="Remove layer", command=self.Remove_layer,bg='lightblue',width=10).grid(row=self.row_offset+6,column=self.button_column, columnspan=self.column_button_span)
        self.angle_scale=tk.Scale(self.sideframe, from_=self.angle_min, to=self.angle_max, resolution=self.angle_step, orient='horizontal', var=self.angle, command=self.Change_angle,bg='#ffd408',length=122)
        self.angle_scale.grid(row=self.row_offset+7,column=self.button_column, columnspan=self.column_button_span)
        tk.Label(self.sideframe, text="Change the input\nangle (°) of light\nreferenced to air",bg= '#ffd408',width=15).grid(row=self.row_offset+8,column=self.button_column, columnspan=self.column_button_span)
        tk.Button(self.sideframe, image=self.buttonleft,command=lambda itemlist=self.step_list:self.decrease_step(itemlist),bg='lightblue').grid(row=self.row_offset+9,column=self.button_column)
        tk.Button(self.sideframe, image=self.buttonright,command=lambda itemlist=self.step_list:self.increase_step(itemlist),bg='lightblue').grid(row=self.row_offset+9,column=self.button_column+2)
        tk.Label(self.sideframe, textvariable=self.step, borderwidth=2,relief=tk.GROOVE, width=10).grid(row=self.row_offset+9,column=self.button_column+1)
        tk.Label(self.sideframe, text="Change the\nwavelength\nstep for the\nsimulation (nm)",bg='lightblue',width=15).grid(row=self.row_offset+10,column=self.button_column, columnspan=self.column_button_span)
        tk.Label(self.sideframe, text="Simulation\nwavelength\nrange is (nm):",width=15,bg='lightgray').grid(row=self.row_offset+11,column=self.button_column, columnspan=self.column_button_span)
        tk.Label(self.sideframe, textvariable=self.range, borderwidth=2,relief=tk.GROOVE, width=15).grid(row=self.row_offset+12,column=self.button_column,columnspan=self.column_button_span)
        tk.Button(self.sideframe, text="Run simulation", command=self.Run_sim,bg='lightgreen',width=10).grid(row=self.row_offset+13,column=self.button_column, columnspan=self.column_button_span)
        

#function that checks that input thickness is only valid positive float numbers larger than zero
#see more at https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
    def Check_input_thickness(self,inStr,acttyp):
        self.error.set('')
        self.errormsg.set('\n')
        if acttyp == '1': #insert
            try:
                float(inStr)
                if float(inStr)==0:#this prevents that input string starts with zero so user can't set layer thickness to zero
                    return False
            except:
                return False #it returns only true of false allowing or not allwing the insert action
        return True

    def decrease_step(self,itemlist):
        self.decrease_list(itemlist)
        self.set_range(0)
        
    def decrease_list(self,itemlist):
        self.error.set('')
        self.errormsg.set('\n')
        if self.step_counter==0:
            self.step_counter=len(itemlist)-1
        else:
            self.step_counter-=1
        self.step.set(itemlist[self.step_counter])

    def increase_step(self,itemlist):
        self.increase_list(itemlist)
        self.set_range(0)
        
    def increase_list(self,itemlist):
        self.error.set('')
        self.errormsg.set('\n')
        if self.step_counter==len(itemlist)-1:
            self.step_counter=0
        else:
            self.step_counter+=1
        self.step.set(itemlist[self.step_counter])

    def Get_structure(self):
        self.layerstructure=container();
        self.layerstructure.layernames=[]
        self.layerstructure.layernames=self.layer_name_list#generic layer names added here
        self.layerstructure.units=[] # thickness units
        self.layerstructure.thickness=[] #thicknesses
        self.layerstructure.layermaterial=[]#layer materials needed to get optical data and to rebuild structure
        self.layerstructure.mat_id=[]#material ID needed to get optical data
        self.layerstructure.layerprop=[] # coh ncoh
        self.layerstructure.Thin=self.angle_scale.get()#input angle needed
        self.layerstructure.absorption_layer=self.absorption_layer.get()#absorption layer
        self.layerstructure.range=self.range.get()
        self.layerstructure.step=float(self.step.get())
        self.layerstructure.wlength_units=[]#for the units of wavelegnths for optical data of materials

        self.error.set('')
        self.errormsg.set('\n')
        for i in range(0,self.layer_counter):
            self.layerstructure.units.append(self.layer_unit_list[i].get())#units of thickness
            self.layerstructure.thickness.append(float(self.layer_thick_list[i].get()))#thickness itself
            self.layerstructure.layerprop.append(self.layer_coh_list[i].get())#coh or ncoh
            self.layerstructure.layermaterial.append(self.layer_mat_list[i].get())#material as string name
            self.layerstructure.mat_id.append(self.mat_id[self.layerstructure.layermaterial[i]]) #stack of materials as ID from database
            self.layerstructure.wlength_units.append(self.wlength_unit[self.layerstructure.mat_id[i]])

    def Process_structure(self):
        senddata=container()
        senddata.Thin=self.layerstructure.Thin*np.pi/180 #in radians
        senddata.layernames=self.layerstructure.layernames
        senddata.layerprop=self.layerstructure.layerprop
        senddata.absorption_layer=self.layerstructure.absorption_layer
        senddata.thickness=np.array([])
        senddata.wlength=[]
        senddata.N=[]
        fitw=self.determine_range()
        for i in range(0,self.layer_counter):
            senddata.thickness=np.append(senddata.thickness,self.convert_units(self.layerstructure.thickness[i],self.layerstructure.units[i]))#using np.append approach to fill in senddata.thickness
            tmp=np.array(ODB_class().get_data(self.conn,self.layerstructure.mat_id[i]))
            tmp=tmp[tmp[:,0].argsort()]#this sorts the data from min wlength to max just in case
            wlength=self.convert_units(tmp[:,0],self.layerstructure.wlength_units[i])
            wlength=wlength.round(11)
            nfit = ipl.interp1d(wlength, tmp[:,1])
            kfit = ipl.interp1d(wlength, tmp[:,2])
            senddata.wlength.append(fitw)
            senddata.N.append(nfit(fitw)-1j*kfit(fitw))
        senddata.wlength=np.array(senddata.wlength)
        senddata.N=np.array(senddata.N)
        return senddata

    def convert_units(self,data,unit):
        #out=None#data is np.array unit is a lis
        if unit=='nm':
            out=data*1e-9
        elif unit=='μm':
            out=data*1e-6
        elif unit=='mm':
            out=data*1e-3
        elif unit=='m':
            out=data
        return out

    def Rebuild_structure(self):#we need to have self.layerstructure
        self.init_mat_window()
        if len(self.layerstructure.layernames)>=2:
            for i in range (1,len(self.layerstructure.layernames)-1):
                self.Add_layer()
                self.layer_coh_list[i].set(self.layerstructure.layerprop[i])
                self.layer_unit_list[i].set(self.layerstructure.units[i])
                self.layer_thick_list[i].delete(0,tk.END)
                self.layer_thick_list[i].insert(tk.END,self.layerstructure.thickness[i])
        self.angle_scale.set(self.layerstructure.Thin)
        self.absorption_layer.set(self.layerstructure.absorption_layer)
        self.range.set(self.layerstructure.range)
        self.step.set(self.layerstructure.step)
        self.step_counter=self.step_list.index(self.layerstructure.step)
        for i in range (0,len(self.layerstructure.layernames)):
            self.layer_mat_list[i].set(self.layerstructure.layermaterial[i])

    def Change_angle(self,val):
        self.error.set('')
        self.errormsg.set('\n')
        #val is the value of the angle and it has to be passed on here as this is lambda function
        self.label_image.destroy()
        self.Add_input_light()

    def Remove_layer(self):
        self.error.set('')
        self.errormsg.set('\n')
        if self.layer_counter>2:
            self.material_Menu[-2].destroy()
            self.layer_mat_list.pop(-2)
            self.material_Menu.pop(-2)
            self.material_Menu[-1].grid(row=self.layer_counter+self.row_offset+1)
            self.coh_Menu[-2].destroy()
            self.layer_coh_list.pop()
            self.coh_Menu.pop(-2)
            self.coh_Menu[-1].grid(row=self.layer_counter+self.row_offset+1)
            self.unit_Menu[-2].destroy()
            self.layer_unit_list.pop()
            self.unit_Menu.pop(-2)
            self.unit_Menu[-1].grid(row=self.layer_counter+self.row_offset+1)
            self.name_Menu[-2].destroy()
            self.name_Menu.pop(-2)
            if self.layer_name_list[-2]==self.absorption_layer.get():
                if self.layer_counter>3:
                    self.absorption_layer.set(self.layer_name_list[-3])
                else:
                    self.absorption_layer.set('None')
            self.layer_name_list.pop(-2)
            self.name_Menu[-1].grid(row=self.layer_counter+self.row_offset+1)
            self.layer_thick_list[-2].destroy()
            self.layer_thick_list.pop(-2)
            self.thick_Menu[-1].grid(row=self.layer_counter+self.row_offset+1)
            self.absorption_Menu[-2].destroy()
            self.absorption_Menu.pop(-2)
            self.absorption_Menu[-1].grid(row=self.layer_counter+self.row_offset+1)
            self.layer_counter-=1
            self.set_range(0)
        else:
            self.error.set('Error:')
            self.errormsg.set('Minimum of 0 layers\nis allowed.')

    def Add_layer_thickness(self):

        if self.layer_counter==1:
            self.layer_thick_list.append(tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_thick_list[0].set('0')
            self.thick_Menu.append(tk.Label(self.mainframe, text=self.layer_thick_list[0].get()))
            self.thick_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.thick_column)
        elif self.layer_counter==2:
            self.layer_thick_list.append(tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_thick_list[-1].set('0')
            self.thick_Menu.append(tk.Label(self.mainframe, text=self.layer_thick_list[-1].get()))
            self.thick_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.thick_column)
        elif self.layer_counter==3:
#here we are using validationcommand to allow only for entry of numbers
            self.layer_thick_list.insert(-1,tk.Entry(self.mainframe, width=7, selectbackground='#f00',validate="key"))
            self.layer_thick_list[-2]['validatecommand']= (self.layer_thick_list[-2].register(self.Check_input_thickness), '%P','%d')
            self.layer_thick_list[-2].insert(tk.END,100.0)
            self.layer_thick_list[-2].grid(row =self.layer_counter+self.row_offset+1, column =self.thick_column)
            self.thick_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.thick_column)
        else:
#here we are using validationcommand to allow only for entry of numbers
            self.layer_thick_list.insert(-1,tk.Entry(self.mainframe, width=7, selectbackground='#f00',validate="key"))
            self.layer_thick_list[-2]['validatecommand']= (self.layer_thick_list[-2].register(self.Check_input_thickness), '%P','%d')
            self.layer_thick_list[-2].insert(tk.END,self.layer_thick_list[-3].get())
            self.layer_thick_list[-2].grid(row =self.layer_counter+self.row_offset+1, column =self.thick_column)
            self.thick_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.thick_column)

    def Add_layer_thickness_unit(self):
        if self.layer_counter==1:
            self.layer_unit_list.append(tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_unit_list[0].set(self.unit_list[0])
            self.unit_Menu.append(tk.Label(self.mainframe, text=self.layer_unit_list[0].get()))
            self.unit_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.unit_column)
        elif self.layer_counter==2:
            self.layer_unit_list.append(tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_unit_list[-1].set(self.unit_list[0])
            self.unit_Menu.append(tk.Label(self.mainframe, text=self.layer_unit_list[-1].get()))
            self.unit_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.unit_column)
        elif self.layer_counter==3:
            self.layer_unit_list.insert(-1,tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_unit_list[-2].set(self.unit_list[-1])# set the default option for the first one in the list
            self.unit_Menu.insert(-1,tk.OptionMenu(self.mainframe, self.layer_unit_list[-2], *self.unit_list,command=self.empty_action_option))
            self.unit_Menu[-2].grid(row =self.layer_counter+self.row_offset+1, column =self.unit_column)
            self.unit_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.unit_column)
        else:
            self.layer_unit_list.insert(-1,tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_unit_list[-2].set(self.layer_unit_list[-3].get()) # for the last members sets the value of previous memeber
            self.unit_Menu.insert(-1,tk.OptionMenu(self.mainframe, self.layer_unit_list[-2], *self.unit_list,command=self.empty_action_option))
            self.unit_Menu[-2].grid(row =self.layer_counter+self.row_offset+1, column =self.unit_column)
            self.unit_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.unit_column)

    def Add_layer_material(self):
        self.layer_mat_list.append(tk.StringVar(self.root)) #storing tkstring var into a list
        if self.layer_counter==1:
            self.layer_mat_list[-1].set(self.mat_list[0])# set the default option for the first one in the list
        else:
            self.layer_mat_list[-1].set(self.layer_mat_list[-2].get()) # for the last members sets the value of previous memeber

        self.material_Menu.append(tk.OptionMenu(self.mainframe, self.layer_mat_list[-1], *self.mat_list, command=self.set_range))#substrate is tested here
        self.material_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.material_column)

    #command automatically gets the value of the string
    def determine_range(self):
        wlengthmin=280e-9 #limist are set with respect to AM1.5 spectrum
        wlengthmax=4000e-9 #limist are set with respect to AM1.5 spectrum
        for i in range(0,self.layer_counter):
            wlengthmin=max(wlengthmin, self.wlength_min[self.mat_id[self.layer_mat_list[i].get()]])
            wlengthmax=min(wlengthmax,self.wlength_max[self.mat_id[self.layer_mat_list[i].get()]])
        range_array=np.arange(wlengthmin,wlengthmax+float(self.step.get())*1e-9/10,float(self.step.get())*1e-9).round(11)
        return range_array

    def set_range(self,idx):
        self.error.set('')
        self.errormsg.set('\n')
        range_array=self.determine_range()
        self.range.set(str(round(range_array[0]*1e9,11))+' - '+str(round(range_array[-1]*1e9,11)))

    def Add_layer_coh(self):
        if self.layer_counter==1:
            self.layer_coh_list.append(tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_coh_list[0].set(self.coh_list[0])
            self.coh_Menu.append(tk.Label(self.mainframe, text=self.layer_coh_list[0].get()))
            self.coh_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.coh_column)
        elif self.layer_counter==2:
            self.layer_coh_list.append(tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_coh_list[-1].set(self.coh_list[0])
            self.coh_Menu.append(tk.Label(self.mainframe, text=self.layer_coh_list[-1].get()))
            self.coh_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.coh_column)
        elif self.layer_counter==3:
            self.layer_coh_list.insert(-1,tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_coh_list[-2].set(self.coh_list[0])# set the default option for the first one in the list
            self.coh_Menu.insert(-1,tk.OptionMenu(self.mainframe, self.layer_coh_list[-2], *self.coh_list,command=self.empty_action_option))
            self.coh_Menu[-2].grid(row =self.layer_counter+self.row_offset+1, column =self.coh_column)
            self.coh_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.coh_column)
        else:
            self.layer_coh_list.insert(-1,tk.StringVar(self.root)) #storing tkstring var into a list
            self.layer_coh_list[-2].set(self.layer_coh_list[-3].get()) # for the last members sets the value of previous memeber
            self.coh_Menu.insert(-1,tk.OptionMenu(self.mainframe, self.layer_coh_list[-2], *self.coh_list,command=self.empty_action_option))
            self.coh_Menu[-2].grid(row =self.layer_counter+self.row_offset+1, column =self.coh_column)
            self.coh_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.coh_column)

    def empty_action_option(self,idx):
        self.error.set('')
        self.errormsg.set('\n')
        
    def empty_action_radio(self):
        self.error.set('')
        self.errormsg.set('\n')

    def Add_absorption_layer(self):
        if self.layer_counter==1:
            self.absorption_layer.set('None')
            self.absorption_Menu.append(tk.Radiobutton(self.mainframe, variable=self.absorption_layer, value=self.layer_name_list[self.layer_counter-1], state=tk.DISABLED))
            self.absorption_Menu[0].grid(row=self.layer_counter+self.row_offset+2, column=self.absorption_column)
        elif self.layer_counter==2:
            self.absorption_Menu.append(tk.Radiobutton(self.mainframe, variable=self.absorption_layer, value=self.layer_name_list[self.layer_counter-1], state=tk.DISABLED))
            self.absorption_Menu[-1].grid(row=self.layer_counter+self.row_offset+2, column=self.absorption_column)
        elif self.layer_counter==3:
            self.absorption_Menu.insert(-1,tk.Radiobutton(self.mainframe, variable=self.absorption_layer, value=self.layer_name_list[-2], state=tk.NORMAL,command=self.empty_action_radio))
            self.absorption_Menu[-2].invoke()
            self.absorption_Menu[-2].grid(row =self.layer_counter+self.row_offset+1, column =self.absorption_column)
            self.absorption_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.absorption_column)
        else:
            self.absorption_Menu.insert(-1,tk.Radiobutton(self.mainframe, variable=self.absorption_layer, value=self.layer_name_list[-2], state=tk.NORMAL,command=self.empty_action_radio))
            self.absorption_Menu[-2].deselect()
            self.absorption_Menu[-2].grid(row =self.layer_counter+self.row_offset+1, column =self.absorption_column)
            self.absorption_Menu[-1].grid(row =self.layer_counter+self.row_offset+2, column =self.absorption_column)

    def Add_name_Menu(self):
        if self.layer_counter==1:
            self.name_Menu.append(tk.Label(self.mainframe, text=self.layer_name_list[0], borderwidth=0,relief=tk.GROOVE))
            self.name_Menu[0].grid(row=self.layer_counter+self.row_offset+2, column=self.name_column)
        elif self.layer_counter==2:
            self.name_Menu.append(tk.Label(self.mainframe, text=self.layer_name_list[-1], borderwidth=0,relief=tk.GROOVE))
            self.name_Menu[-1].grid(row=self.layer_counter+self.row_offset+2, column=self.name_column)
        else:
            self.layer_name_list.insert(-1,'Layer '+str(self.layer_counter-2))
            self.name_Menu.insert(-1,tk.Label(self.mainframe, text=self.layer_name_list[-2], borderwidth=2,relief=tk.GROOVE))
            self.name_Menu[-2].grid(row=self.layer_counter+self.row_offset+1, column=self.name_column)
            self.name_Menu[-1].grid(row=self.layer_counter+self.row_offset+2, column=self.name_column)

    def Add_layer(self):
        self.error.set('')
        self.errormsg.set('\n')
        self.layer_counter+=1
        if self.layer_counter<12:
        # Create a Tkinter variable
            self.Add_layer_material()
            self.Add_name_Menu()
            self.Add_layer_coh()
            self.Add_layer_thickness_unit()
            self.Add_layer_thickness()
            self.Add_absorption_layer()
        else:
            self.layer_counter-=1
            self.error.set('Error:')
            self.errormsg.set('Maximum of 9 layers\nis allowed.')


    def Add_input_light(self):
        dirname=os.path.dirname(__file__)#path of this __file__ not the __main__
        imagepath=os.path.join(dirname, 'images', "Arrow"+str(int(self.angle.get()))+".png")
        image = Image.open(imagepath)
        self.image=ImageTk.PhotoImage(image)#saving the reference
        self.label_image = tk.Label(self.mainframe, image=self.image)
        #self.label_image.image=image#saving the reference in a different way
        self.label_image.grid(row=2,column=self.name_column)

    def Add_title_labels(self):
        label=tk.Label(self.mainframe, text='Materials available with format:\n  "Name:Range(Unit)[Number of Entries]"  ', wraplength=450, borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=self.material_column)

        label=tk.Label(self.mainframe, text='Structure layout with\ngeneric layer names', wraplength=450, borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=self.name_column)

        label=tk.Label(self.mainframe, text='Set coherence\n of layers', wraplength=450, borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=self.coh_column)

        label=tk.Label(self.mainframe, text='Set layer thickness\nunits', wraplength=450, borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=self.unit_column)

        label=tk.Label(self.mainframe, text='Input layer\nthickness', wraplength=450, borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=self.thick_column)

        label=tk.Label(self.mainframe, text='Available\ncommands', width=15, wraplength=450, borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=self.button_column, columnspan=self.column_button_span)

        label=tk.Label(self.mainframe, text='Select the\nactive layer', wraplength=450, borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=self.absorption_column)


    def Run_sim(self):
        self.Get_structure()
        senddata=self.Process_structure()
        self.result=ncohTMM().main_calc(senddata)
        self.result.step=self.layerstructure.step
        self.result.wlength=senddata.wlength[0,:]
        self.result.layernames=senddata.layernames
        self.result.absorption_layer=senddata.absorption_layer
        self.procceseddata=PostProcess.main_calc(PostProcess(),self.result)
        self.init_result_window()

#result window stuff
        
    def init_result_window(self):
        self.mainframe.destroy()
        self.init_mainframe()
        self.init_sideframe()
        self.Add_result_labels()
        self.Add_buttons_result()
        self.init_fig()
        self.init_canvas()
        self.plotting_figs()
    
    def init_canvas(self):    
        self.canvas=FigureCanvasTkAgg(self.plot.fig,master=self.mainframe)
        self.canvas.get_tk_widget().grid(row=self.row_offset+4,column=self.material_column)
        self.canvas.draw()
        toolbar = NavigationToolbar2Tk(self.canvas, self.mainframe, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=self.row_offset+5,column=self.material_column)
        
    def init_fig(self):
        self.color_list=['red','blue','black','lightgray','white']
        
        if self.result.plosspickup:
            self.plot=TMMfigurefull()
            self.plot.axtr.set_xlim(self.result.P_z[0]*1e9,self.result.P_z[-1]*1e9)
            self.plot.axbr.set_xlim(self.result.P_z[0]*1e9,self.result.P_z[-1]*1e9)
            self.plot.axtr.set_ylim(0.9*min(np.min(self.procceseddata.Gs),np.min(self.procceseddata.Gp)),0.1*min(np.min(self.procceseddata.Gs),np.min(self.procceseddata.Gp))+max(np.max(self.procceseddata.Gs),np.max(self.procceseddata.Gp))+0.5)
            idx=int((self.angle.get()-self.result.wlength[0]*1e9)/self.result.step)
            self.plot.axbr.set_ylim(0.9*min(np.min(self.procceseddata.singleGs[:,idx]),np.min(self.procceseddata.singleGp[:,idx])),0.1*min(np.min(self.procceseddata.singleGs[:,idx]),np.min(self.procceseddata.singleGp[:,idx]))+max(np.max(self.procceseddata.singleGs[:,idx]),np.max(self.procceseddata.singleGp[:,idx]))+0.5)#0.5 is for the case when there is really no absorption in the active layer
        else:
            self.plot=TMMfigure()
        self.plot.axtl.set_xlim(self.result.wlength[0]*1e9,self.result.wlength[-1]*1e9)
        self.plot.axtl.set_ylim(0,1.01)
        self.plot.axbl.set_xlim(self.result.wlength[0]*1e9,self.result.wlength[-1]*1e9)
        self.plot.axbl.set_ylim(0,1)
        
        
    def plotting_figs(self):
        try:
            self.plot.axtl.lines.pop(-1)
            self.plot.axtl.lines.pop(-1)
            self.plot.axtr.lines.pop(-1)
            self.plot.axbr.lines.pop(-1)
            self.plot.axtl.get_legend().remove()#removing a legend
            self.plot.axbl.collections.pop(-1)
            self.plot.axbl.collections.pop(-1)
            self.plot.axbl.collections.pop(-1)
            self.plot.axbl.collections.pop(-1)
            self.plot.axbl.collections.pop(-1)
        except:
            pass
        idx=int((self.angle.get()-self.result.wlength[0]*1e9)/self.result.step)
        if self.step.get()=='p':
            if self.result.absorption_layer!='None':
                curridx=self.result.layernames.index(self.result.absorption_layer)
                current=self.procceseddata.current_p[curridx]
            else:
                current=0
            self.plot_one_polarization('p',self.result.Rp,self.result.Tp,self.procceseddata.sorted_p,current)
            if self.result.plosspickup:
                curridx=self.result.layernames.index(self.result.absorption_layer)
                
                self.plot.axbr.set_title(r'$\lambda$ = '+str(self.angle.get())+' nm', fontsize=10)
                self.plot.axtr.plot(self.result.P_z*1e9,self.procceseddata.Gp,'black')
                self.plot.axbr.plot(self.result.P_z*1e9,self.procceseddata.singleGp[:,idx],'black')
        elif self.step.get()=='s':
            if self.result.absorption_layer!='None':
                curridx=self.result.layernames.index(self.result.absorption_layer)
                current=self.procceseddata.current_s[curridx]
            else:
                current=0
            self.plot_one_polarization('s',self.result.Rs,self.result.Ts,self.procceseddata.sorted_s,current)
            if self.result.plosspickup:
                self.plot.axbr.set_title(r'$\lambda$ = '+str(self.angle.get())+' nm', fontsize=10)
                self.plot.axtr.plot(self.result.P_z*1e9,self.procceseddata.Gs,'black')
                self.plot.axbr.plot(self.result.P_z*1e9,self.procceseddata.singleGs[:,idx],'black')
        elif self.step.get()=='average':
            if self.result.absorption_layer!='None':
                curridx=self.result.layernames.index(self.result.absorption_layer)
                current=self.procceseddata.current_avg[curridx]
            else:
                current=0
            self.plot_one_polarization('average',self.result.Ravg,self.result.Tavg,self.procceseddata.sorted_avg,current)
            if self.result.plosspickup:
                self.plot.axbr.set_title(r'$\lambda$ = '+str(self.angle.get())+' nm', fontsize=10)
                self.plot.axtr.plot(self.result.P_z*1e9,self.procceseddata.Gavg,'black')
                self.plot.axbr.plot(self.result.P_z*1e9,self.procceseddata.singleGavg[:,idx],'black')

        self.plot.axbl.legend(['Active','Front','Back', 'T', 'R'],loc='upper right',bbox_to_anchor=(1.1, 1.15),framealpha=0.5)
            
        self.canvas.draw()
        
    def plot_one_polarization(self,pol,R,T,A,current):
        self.absorption_layer.set(round(current,2))
        self.plot.fig.suptitle(pol+' - polarization')
        self.plot.axtl.plot(self.result.wlength*1e9,1-R,'red')
        self.plot.axtl.plot(self.result.wlength*1e9,T,'blue')
        self.plot.axtl.legend([r'1-R',r'T'],loc='lower right')
        for idx in range(0,np.shape(A)[0]-1):
            self.plot.axbl.fill_between(self.result.wlength*1e9,A[idx,:],A[idx+1,:],color=self.color_list[idx])
        
    
    def Add_result_labels(self):
        label=tk.Label(self.mainframe, text='Available\nplots', wraplength=450, borderwidth=2,relief=tk.GROOVE,width=95)
        label.grid(row = 1, column=self.material_column,columnspan=2)


        label=tk.Label(self.mainframe, text='Available\ncommands', width=20, wraplength=450, borderwidth=2,relief=tk.GROOVE)
        label.grid(row = 1, column=self.button_column, columnspan=self.column_button_span)

        
    def Add_buttons_result(self):
        self.angle.set(self.result.wlength[int(0.5*len(self.result.wlength))]*1e9)
        self.step_counter=1 #we need to reset it
        self.step.set(self.pol_list[self.step_counter])
        self.save_button=tk.Button(self.sideframe, text="Save main results\n and structure for\n all polarizations", command=self.Save_all,width=14,bg='lightgray').grid(row=self.row_offset+1,column=self.button_column, columnspan=self.column_button_span)
        tk.Button(self.sideframe, image=self.buttonleft,command=lambda itemlist=self.pol_list:self.change_pol_left(itemlist),bg='lightblue').grid(row=self.row_offset+2,column=self.button_column)
        tk.Button(self.sideframe, image=self.buttonright,command=lambda itemlist=self.pol_list:self.change_pol_right(itemlist),bg='lightblue').grid(row=self.row_offset+2,column=self.button_column+2)
        tk.Label(self.sideframe, textvariable=self.step, borderwidth=2,relief=tk.GROOVE, width=15).grid(row=self.row_offset+2,column=self.button_column+1)
        tk.Label(self.sideframe, text="Choose the\npolarisation of the\nlight for the figures",bg='lightblue',width=19).grid(row=self.row_offset+3,column=self.button_column, columnspan=self.column_button_span)
        if self.result.plosspickup:
            self.wlength_scale=tk.Scale(self.sideframe, from_=int(self.result.wlength[0]*1e9), to=int(self.result.wlength[-1]*1e9), resolution=int(self.result.step), orient='horizontal', var=self.angle, command=self.update_single_gen,bg='#ffd408',length=155)
            self.wlength_scale.grid(row=self.row_offset+4,column=self.button_column, columnspan=self.column_button_span)
            tk.Label(self.sideframe, text="Change a\nwavelength (nm)\nto select G(z,\u03bb)",bg= '#ffd408',width=19).grid(row=self.row_offset+5,column=self.button_column, columnspan=self.column_button_span)
        
        if self.result.absorption_layer!='None':
            tk.Label(self.sideframe, textvariable=self.absorption_layer,relief=tk.GROOVE,width=15).grid(row=self.row_offset+7,column=self.button_column, columnspan=self.column_button_span)
            tk.Label(self.sideframe, text='Estimated short\ncircuit current\n(mA/cm\u00b2)', width=19).grid(row=self.row_offset+6, column=self.button_column, columnspan=self.column_button_span)
        
        tk.Button(self.sideframe, text="Go back to\nsimulation", command=self.Rebuild_structure,width=14,bg='lightcoral').grid(row=self.row_offset+8,column=self.button_column, columnspan=self.column_button_span)
        
    def update_single_gen(self,val):
        try:
            self.plot.axbr.lines.pop(-1)
        except:
            pass
        idx=int((self.angle.get()-self.result.wlength[0]*1e9)/self.result.step)
        self.plot.axbr.set_title(r'$\lambda$='+str(self.angle.get())+' nm', fontsize=10)
        self.plot.axbr.set_ylim(0.9*min(np.min(self.procceseddata.singleGs[:,idx]),np.min(self.procceseddata.singleGp[:,idx])),0.1*min(np.min(self.procceseddata.singleGs[:,idx]),np.min(self.procceseddata.singleGp[:,idx]))+max(np.max(self.procceseddata.singleGs[:,idx]),np.max(self.procceseddata.singleGp[:,idx]))+0.5)
        
        if self.step.get()=='p': 
            self.plot.axbr.plot(self.result.P_z*1e9,self.procceseddata.singleGp[:,idx],'black')
        elif self.step.get()=='s': 
            self.plot.axbr.plot(self.result.P_z*1e9,self.procceseddata.singleGs[:,idx],'black')
        elif self.step.get()=='average':
            self.plot.axbr.plot(self.result.P_z*1e9,self.procceseddata.singleGavg[:,idx],'black')
        self.canvas.draw()
        
    def change_pol_left(self,itemlist):
        self.decrease_list(itemlist)
        self.plotting_figs()
    
    def change_pol_right(self,itemlist):
        self.increase_list(itemlist)
        self.plotting_figs()

    def Save_all(self):
        filename = asksaveasfilename(title="Select the folder to save the project.", initialdir=self.pjdirectory,filetypes=[("Project files","*.proj")],initialfile=self.PJ_name)
        if filename:
            (self.pjdirectory,self.Pj_name)=os.path.split(filename)
            self.write_to_ini()
            self.Save_structure(filename)
            self.Save_absorption(filename,'s',self.result.As,self.result.Rs,self.result.Ts)
            self.Save_absorption(filename,'p',self.result.Ap,self.result.Rp,self.result.Tp)
            self.Save_absorption(filename,'avg',self.result.Aavg,self.result.Ravg,self.result.Tavg)
            self.Save_currents(filename)
            if self.result.plosspickup:
                self.Save_net_gen_rate(filename)
                self.save_button=tk.Button(self.sideframe, text="Save G(z,\u03bb) for\n chosen wavelength \nand all polarizations", command=self.Save_single_gen_rate,width=14,bg='lightgray').grid(row=self.row_offset+1,column=self.button_column, columnspan=self.column_button_span)
        else:
            pass

    def Save_structure(self,filename):
        write=[]
        text='Database='+self.DB_name
        write.append(text)
        text='Layer_name='
        text=self.Add_items(text,self.layerstructure.layernames,',')
        write.append(text)
        text='Layer_material='
        text=self.Add_items(text,self.layerstructure.layermaterial,',')
        write.append(text)
        text='Layer_coherence='
        text=self.Add_items(text,self.layerstructure.layerprop,',')
        write.append(text)
        text='Layer_thickness='
        text=self.Add_items(text,self.layerstructure.thickness,',')
        write.append(text)
        text='Layer_thickness_units='
        text=self.Add_items(text,self.layerstructure.units,',')
        write.append(text)
        text='Input_angle='+str(self.layerstructure.Thin)
        write.append(text)
        text='Absorption_layer='+self.layerstructure.absorption_layer
        write.append(text)
        text='Simulation_range='+self.layerstructure.range
        write.append(text)
        text='Simulation_step='+str(self.layerstructure.step)
        write.append(text)
        with open(filename,'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
                
    def Save_absorption(self,filename,pol,A,R,T):
        write=[]
        text='wlength (m)\t'
        text=self.Add_items(text,self.layerstructure.layernames,'\t')
        write.append(text)
        data=np.array(A)
        data[0,:]=data[0,:]+R
        data[-1,:]=data[-1,:]+T
        data=np.insert(data,0,self.result.wlength,axis=0)
        fmtlist=[]
        fmtlist.append('%.3e')
        for i in range(1,np.shape(data)[0]):
            fmtlist.append('%.6e')
        with open(filename.replace('.proj','_losses_in_layers_'+pol+'_pol.txt'),'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
            for line in np.transpose(data):
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt=fmtlist)
                
    def Save_net_gen_rate(self,filename):
        write=[]
        text='pos (m)\ts (m\u207b\u00b3s\u207b\u00b9)\tp (m\u207b\u00b3s\u207b\u00b9)\tavg (m\u207b\u00b3s\u207b\u00b9)'
        write.append(text)
        data=np.array([np.round(self.result.P_z,11),self.procceseddata.Gs,self.procceseddata.Gp,self.procceseddata.Gavg])
        with open(filename.replace('.proj','_G(z).txt'),'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
            for line in np.transpose(data):
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt=['%.3e','%.6e','%.6e','%.6e'])


    def Save_currents(self,filename):
        write=[]
        text='\t'
        text=self.Add_items(text,self.layerstructure.layernames,'\t')
        write.append(text)
        data=[]
        line=[''.join(item) for item in np.round(self.procceseddata.current_s,2).astype(str)]
        line.insert(0,'s (mA/cm\u00b2)')
        data.append(line)
        line=[''.join(item) for item in np.round(self.procceseddata.current_p,2).astype(str)]
        line.insert(0,'p (mA/cm\u00b2)')
        data.append(line)
        line=[''.join(item) for item in np.round(self.procceseddata.current_avg,2).astype(str)]
        line.insert(0,'avg (mA/cm\u00b2)')
        data.append(line)
        with open(filename.replace('.proj','_current_losses.txt'),'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
            for line in data:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
                
    def Save_single_gen_rate(self):
        filename=os.path.join(self.pjdirectory,self.Pj_name)
        idx=int((self.angle.get()-self.result.wlength[0]*1e9)/self.result.step)
        write=[]
        text='\u03bb = '+str(self.result.wlength[idx]*1e9)+' nm'
        write.append(text)
        text='pos (m)\ts (m\u207b\u00b3s\u207b\u00b9)\tp (m\u207b\u00b3s\u207b\u00b9)\tavg (m\u207b\u00b3s\u207b\u00b9)'
        write.append(text)
        data=np.array([np.round(self.result.P_z,11),self.procceseddata.singleGs[:,idx],self.procceseddata.singleGp[:,idx],self.procceseddata.singleGavg[:,idx]])
        with open(filename.replace('.proj','_G(z,\u03bb)_'+str(self.result.wlength[idx]*1e9)+'_nm.txt'),'w') as f:
            for line in write:
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt='%s')
            for line in np.transpose(data):
                np.savetxt(f, [line], delimiter='\t', newline='\n', fmt=['%.3e','%.6e','%.6e','%.6e'])
        

if __name__=='__main__':
    LoadData.init_start(LoadData())
