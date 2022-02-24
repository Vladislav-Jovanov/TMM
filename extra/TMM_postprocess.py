#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  6 12:43:23 2022

@author: tzework
"""

import xlrd
import os
import numpy as np


class container():
    pass
#example
#self.xlsfilename=os.path.join('astmg173.xls')
#minimum datain example
#datain.plosspickup
#datain.As
#datain.Ap
#datain.Ps
#datain.Pp
#datain.wlength all wlengths as vector in meters
#datain.step step between wlengths in [nm]

class PostProcess():
    
    def __init__(self):
        self.q=1.602176634e-19;#C
        self.c=299792458;#m/s
        self.h=6.62607015e-34;#Js
        self.xlsfilename=os.path.join(os.path.dirname(__file__),'astmg173.xls')
        
    def main_calc(self,datain):
        outdata=container()
        
        self.wavestep_for_sum(datain.step,datain.wlength)
        self.amspectrum(datain.wlength)
        if datain.plosspickup:
            outdata.Gs=self.net_generation_rate(datain.Ps,datain.wlength)#units m^(-3)s^(-1)
            outdata.Gp=self.net_generation_rate(datain.Pp,datain.wlength)#units m^(-3)s^(-1)
            outdata.Gavg=(outdata.Gs+outdata.Gp)/2#units m^(-3)s^(-1)
            outdata.singleGs=self.single_generation_rate(datain.Ps,datain.wlength)#units m^(-3)s^(-1)
            outdata.singleGp=self.single_generation_rate(datain.Pp,datain.wlength)#units m^(-3)s^(-1)
            outdata.singleGavg=(outdata.singleGs+outdata.singleGp)/2#units m^(-3)s^(-1)
        
        outdata.current_s=self.current_calc_all(datain.As,datain.Ts,datain.Rs,datain.wlength)#current is in mA/cm2
        outdata.current_p=self.current_calc_all(datain.Ap,datain.Tp,datain.Rp,datain.wlength)#current is in mA/cm2
        outdata.current_avg=(outdata.current_s+outdata.current_p)/2#current is in mA/cm2
        outdata.sorted_s=self.process_layers(datain.As,datain.Ts,datain.Rs,datain.layernames,datain.absorption_layer)
        outdata.sorted_p=self.process_layers(datain.Ap,datain.Tp,datain.Rp,datain.layernames,datain.absorption_layer)
        outdata.sorted_avg=(outdata.sorted_s+outdata.sorted_p)/2
        return outdata
        
    def process_layers(self,A,T,R,layernames,absorptionlayer):
        sort=[]
        #try to find an index
        try:
            idx=layernames.index(absorptionlayer)
        except:
            idx=-1 #if it doesn't exist put negatice there
        
        if idx!=-1:
            sort.append(0*A[idx,:]) # we plot between the lines and we need to have zero to start with
            sort.append(A[idx,:])
            sort.append(sort[-1]+A[1:idx].sum(axis=0))
            sort.append(sort[-1]+A[idx+1:].sum(axis=0))#[idx+1:] means till the end [idx+1:-1] means not the last one
        else:
            sort.append(0*A[0,:])
            sort.append(0*A[0,:])
            sort.append(0*A[0,:])
            sort.append(0*A[0,:])
               
        sort.append(sort[-1]+T)
        sort.append(sort[-1]+R+A[0,:])
        return np.array(sort)
            
    def wavestep_for_sum(self,step,wlength):
        deltaw=[]
        for item in wlength:
            deltaw.append(step)
        deltaw[0]=step/2;
        deltaw[-1]=step/2;
        self.deltaw=np.array(deltaw)
    
    def amspectrum(self,wlength):
        workbook = xlrd.open_workbook(self.xlsfilename)
        sheet = workbook.sheet_by_name(workbook.sheet_names()[1])
        spectrum=[]
        for item in wlength:
            for row in range(0,sheet.nrows):
                if round(item*1e9,11)==sheet.cell_value(rowx=row, colx=0):
                    spectrum.append(sheet.cell_value(rowx=row, colx=2))
        self.spectrum=np.array(spectrum)
        
    def net_generation_rate(self,P,wlength):
        gen_rate=np.zeros(np.shape(P)[0])
        for i in range(0,np.shape(P)[1]):
            gen_rate=gen_rate+wlength[i]*self.spectrum[i]*P[:,i]*self.deltaw[i]/(self.h*self.c)
        return gen_rate
    
    def single_generation_rate(self,P,wlength):
        gen_rate=np.zeros(np.shape(P))
        for i in range(0,np.shape(P)[1]):
            gen_rate[:,i]=wlength[i]*self.spectrum[i]*P[:,i]/(self.h*self.c)
        return gen_rate

    def current_calc_all(self,A,T,R,wlength):
        #you are not allowed to make changes to A and you need to break connection changes to A would go outside of this function which is stupid
        Btmp=np.array(A)#this way no changes will be transffered to A
        Btmp[0,:]=Btmp[0,:]+R#this way fist current will represent all loses in input media
        Btmp[-1,:]=Btmp[-1,:]+T#this way last current will represent all loses in exit media
        current=[]
        for i in range(0,np.shape(Btmp)[0]):
            tmp=self.q*wlength*self.spectrum*Btmp[i,:]*self.deltaw/(self.h*self.c)
            tmp=tmp.sum()
            current.append(round(tmp,11))
        return np.array(current)/10 #unit mA/cm2
    
    
    def current_calc(self,A,step,wlength):
        self.wavestep_for_sum(step,wlength)
        self.amspectrum(wlength)
        current=self.q*wlength*self.spectrum*A*self.deltaw/(self.h*self.c)
        current=current.sum()
        return current/10
        