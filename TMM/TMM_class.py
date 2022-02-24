#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 22:18:33 2021

@author: tzework
"""
import numpy as np


#how complex refractive index is defined
#def cmp_index(n,k):
#    N=n-k*1j;
#    return N;

class container():
    pass;


#example of input data for ncohTMM
#a=container();
#a.Thin=45*np.pi/180;#convert to radian
#a.N=np.array([[1-1j*0,1-1j*0],[1.5-1j*0,1.5-1j*0],[1.68632-1j*0.51749, 2.14843-1j*0.29105],[1-1j*0,1-1j*0]]);
#a.wlength=np.array([[470,570],[470,570],[470,570],[470,570]])*1e-9;#in meters
#a.thickness=np.array([0,3e6,100,0])*1e-9;#in meters
#a.layernames=["Input media","Layer 1","Layer 2","Exit media"];#names of layers
#a.absorption_layer="Layer 2";#index of layer
#a.layerprop=["coh","ncoh","coh","coh"];#first and last are always coh but they are used as ncoh too

#example of input data for cohTMM are np.array for N(complex index) and for wavelengths
#list of layernames
#input angle in radians
#np.array layer thickness
#absorption layername
#by default wavelength and thickness units should be the same
#this is input for cohTMM class
#a=container();
#a.Thin=45*np.pi/180;
#a.N=np.array([[1-1j*0,1-1j*0],[1.68632-1j*0.51749, 2.14843-1j*0.29105],[1.5-1j*0,1.5-1j*0]]);
#a.wlength=np.array([[470,570],[470,570],[470,570]])*1e-9;
#a.thickness=np.array([[0,0],[100,100],[0,0]])*1e-9;
#a.layernames=["Input media","Layer 1","Layer 2","Exit media"];
#a.absorption_layer="Layer 2";



class cohTMM():
    
    def __init__(self):
        pass;
        
    def main_calc(self,datain):
        self.outdata=container();
        self.Thin=datain.Thin;
        self.N=datain.N;#same shape
        self.wlength=datain.wlength;#same shape
        self.thickness=datain.thickness;#same shape
        self.layernames=datain.layernames;
        self.absorption_layer=datain.absorption_layer;
        self.get_layer_index();
        self.Snell();
        
        if self.IDX:
            self.outdata.Rs, self.outdata.Ts, self.outdata.As, self.outdata.Ps = self.R_T_A_P_calc_s();
            self.outdata.Rp, self.outdata.Tp, self.outdata.Ap, self.outdata.Pp = self.R_T_A_P_calc_p();
        else:
            self.outdata.Rs, self.outdata.Ts, self.outdata.As = self.R_T_A_P_calc_s();
            self.outdata.Rp, self.outdata.Tp, self.outdata.Ap = self.R_T_A_P_calc_p();
        #reverese order of layers
        self.N=np.flip(self.N, axis=0);
        self.thickness=np.flip(self.thickness, axis=0);
        self.layernames.reverse();
        self.get_layer_index();
        self.Snell();
        
        if self.IDX:
            self.outdata.Rsrev, self.outdata.Tsrev, self.outdata.Asrev, self.outdata.Psrev = self.R_T_A_P_calc_s();
            self.outdata.Rprev, self.outdata.Tprev, self.outdata.Aprev, self.outdata.Pprev = self.R_T_A_P_calc_p();
            self.outdata.Psrev=np.flip(self.outdata.Psrev,axis=0);
            self.outdata.Pprev=np.flip(self.outdata.Pprev,axis=0);
        else:
            self.outdata.Rsrev, self.outdata.Tsrev, self.outdata.Asrev = self.R_T_A_P_calc_s();
            self.outdata.Rprev, self.outdata.Tprev, self.outdata.Aprev = self.R_T_A_P_calc_p();
        
        self.outdata.Asrev=np.flip(self.outdata.Asrev,axis=0);#remeber this error :P
        self.outdata.Aprev=np.flip(self.outdata.Aprev,axis=0);#
        
        return self.outdata;
    
    def get_layer_index(self):
        try:
            IDX=self.layernames.index(self.absorption_layer);
            test=np.imag(self.N[IDX,:])==0#tests that absorption layer is absorbing
            if test.all():
                absorbing=False #active layer doesn't absorb
            else:
                absorbing=True #active layer absorbs
        except:
            IDX=0
        if (IDX!=0 and IDX!=len(self.layernames)-1 and absorbing): #IDX can't be first or last in the layer list that means it is non coherent
            self.IDX=IDX;
        else:
            self.IDX=0;
            
        self.outdata.plosspickup=bool(self.IDX);
        
    def Snell(self):
        self.Th=np.arcsin(np.sin(self.Thin)/self.N);
    #for reverse reverse self.N and self.Th and self.thickness and self.layername beforehand
    def Fresnel_p(self):
        rp=(self.N[0:-1,:]*np.cos(self.Th[1:,:])-self.N[1:,:]*np.cos(self.Th[0:-1,:]))/(self.N[0:-1,:]*np.cos(self.Th[1:,:])+self.N[1:,:]*np.cos(self.Th[0:-1,:]));
        tp=2*self.N[0:-1,:]*np.cos(self.Th[0:-1,:])/(self.N[0:-1,:]*np.cos(self.Th[1:,:])+self.N[1:,:]*np.cos(self.Th[0:-1,:]));
        return (rp,tp);
    #for reverse reverse self.N and self.Th and self.thickness and self.layername beforehand
    def Fresnel_s(self):
        rs=(self.N[0:-1,:]*np.cos(self.Th[0:-1,:])-self.N[1:,:]*np.cos(self.Th[1:,:]))/(self.N[0:-1,:]*np.cos(self.Th[0:-1,:])+self.N[1:,:]*np.cos(self.Th[1:,:]));
        ts=2*self.N[0:-1,:]*np.cos(self.Th[0:-1,:])/(self.N[0:-1,:]*np.cos(self.Th[0:-1,:])+self.N[1:,:]*np.cos(self.Th[1:,:]));
        return (rs, ts);
    #it needs input agruments so it can be used for all r,t we have
    def Poyntingamps(self,r,t):#r,t is output of Fresnel_p or Fresnel_s
        phi=np.exp(-1j*2*np.pi*self.N*np.cos(self.Th)*self.thickness/self.wlength);
        rc=np.ones(np.shape(self.N))*(0+1j*0);
        tc=np.ones(np.shape(self.N))*(1+1j*0);
        tamp=np.ones(np.shape(self.N))*(1+1j*0);
        ramp=np.ones(np.shape(self.N))*(0+1j*0);
        
        for ii in range(0,np.shape(r)[0]):
            rc[-2-ii,:]=(r[-1-ii,:]+rc[-1-ii,:]*phi[-1-ii,:]*phi[-1-ii,:])/(1+r[-1-ii,:]*rc[-1-ii,:]*phi[-1-ii,:]*phi[-1-ii,:]);
            tc[-1-ii,:]=t[-1-ii,:]/(1+r[-1-ii,:]*rc[-1-ii,:]*phi[-1-ii,:]*phi[-1-ii,:]);
        for ii in range(1,np.shape(tc)[0]):
            tamp[ii,:]=tamp[ii-1,:]*phi[ii-1,:]*tc[ii,:];
        for ii in range(0,np.shape(rc)[0]):
            ramp[ii,:]=tamp[ii]*phi[ii,:]*phi[ii,:]*rc[ii,:]; 
        return (ramp,tamp);
        
    def R_T_A_P_calc_s(self):
        ramp,tamp=self.Poyntingamps(*self.Fresnel_s());
        R=np.real(ramp[0,:]*np.conj(ramp[0,:]));
        T=np.real(tamp[-1,:]*np.conj(tamp[-1,:]))*np.real(np.conj(self.N[-1,:])*np.conj(np.cos(self.Th[-1,:])))/np.real(np.conj(self.N[0,:])*np.conj(np.cos(self.Th[0,:])))
        S=np.ones(np.shape(self.N));
        A=np.zeros(np.shape(self.N));#thic needs to be zeros
        
        for ii in range(1,np.shape(self.N)[0]):
            S[ii,:]=np.real(np.conj(self.N[ii,:])*np.conj(np.cos(self.Th[ii,:]))*(tamp[ii,:]+ramp[ii,:])*(np.conj(tamp[ii,:])-np.conj(ramp[ii,:])))/np.real(np.conj(self.N[0,:])*np.conj(np.cos(self.Th[0,:])));
            A[ii-1,:]=S[ii-1,:]-S[ii,:];
        A[0,:]=A[0,:]-R;

        P=np.zeros((101,np.shape(self.N)[1]));
        if self.IDX:
            for jj in range(0,np.shape(self.N[self.IDX])[0]):
                kjz=2*np.pi*self.N[self.IDX,jj]*np.cos(self.Th[self.IDX,jj])/self.wlength[self.IDX,jj];
                z=np.linspace(0,self.thickness[self.IDX,jj],101);
                prefact=-np.real(self.N[self.IDX,jj])*np.imag(self.N[self.IDX,jj])*4*np.pi/(self.wlength[self.IDX,jj]*np.real(np.conj(self.N[0,jj])*np.conj(np.cos(self.Th[0,jj]))));
                for ii in range(0,101):
                    P[ii,jj]=prefact*np.real((tamp[self.IDX,jj]*np.exp(-1j*z[ii]*kjz)+ramp[self.IDX,jj]*np.exp(1j*z[ii]*kjz))*np.conj(tamp[self.IDX,jj]*np.exp(-1j*z[ii]*kjz)+ramp[self.IDX,jj]*np.exp(1j*z[ii]*kjz)));
            
            self.outdata.P_z=z;#you need to asign this only once for forward or backward s or p
            return R,T,A,P;
        else:
            return R,T,A;
    
    def R_T_A_P_calc_p(self):
        ramp,tamp=self.Poyntingamps(*self.Fresnel_p());
        R=np.real(ramp[0,:]*np.conj(ramp[0,:]));
        T=np.real(tamp[-1,:]*np.conj(tamp[-1,:]))*np.real(np.conj(self.N[-1,:])*np.cos(self.Th[-1,:]))/np.real(np.conj(self.N[0,:])*np.cos(self.Th[0,:]));
        S=np.ones(np.shape(self.N));
        A=np.zeros(np.shape(self.N));#this needs to be zeros
        
        for ii in range(1,np.shape(self.N)[0]):
            S[ii,:]=np.real(np.conj(self.N[ii,:])*np.cos(self.Th[ii,:])*(tamp[ii,:]+ramp[ii,:])*(np.conj(tamp[ii,:])-np.conj(ramp[ii,:])))/np.real(np.conj(self.N[0,:])*np.cos(self.Th[0,:]));
            A[ii-1,:]=S[ii-1,:]-S[ii,:];
        A[0,:]=A[0,:]-R;
        
        P=np.zeros((101,np.shape(self.N)[1]));
        if self.IDX:
            for jj in range(0,np.shape(self.N[self.IDX])[0]):
                kjz=2*np.pi*self.N[self.IDX,jj]*np.cos(self.Th[self.IDX,jj])/self.wlength[self.IDX,jj];
                z=np.linspace(0,self.thickness[self.IDX,jj],101);
                prefact=-np.real(self.N[self.IDX,jj])*np.imag(self.N[self.IDX,jj])*4*np.pi/(self.wlength[self.IDX,jj]*np.real(np.conj(self.N[0,jj])*np.cos(self.Th[0,jj])));
                for ii in range(0,101):    
                    P[ii,jj]=prefact*(np.real(((tamp[self.IDX,jj]*np.exp(-1j*z[ii]*kjz)+ramp[self.IDX,jj]*np.exp(1j*z[ii]*kjz))*np.cos(self.Th[self.IDX,jj]))*np.conj((tamp[self.IDX,jj]*np.exp(-1j*z[ii]*kjz)+ramp[self.IDX,jj]*np.exp(1j*z[ii]*kjz))*np.cos(self.Th[self.IDX,jj])))+np.real(((tamp[self.IDX,jj]*np.exp(-1j*z[ii]*kjz)-ramp[self.IDX,jj]*np.exp(1j*z[ii]*kjz))*np.sin(self.Th[self.IDX,jj]))*np.conj((tamp[self.IDX,jj]*np.exp(-1j*z[ii]*kjz)-ramp[self.IDX,jj]*np.exp(1j*z[ii]*kjz))*np.sin(self.Th[self.IDX,jj]))));
            
            return R,T,A,P;
        else:
            return R,T,A;


class ncohTMM():
    def __init__(self):
        pass;
    
    def main_calc(self,datain):
        self.outdata=container();
        self.process_structure(datain);
 
        tmmdata=self.cohtmm_run(datain);
        self.outdata.plosspickup=tmmdata.plosspickup;
        Th=np.arcsin(np.sin(datain.Thin)/self.structure.Nnc);
        absphi=np.real(np.exp(-1j*2*np.pi*self.structure.Nnc*np.cos(Th)*self.structure.thicknc/self.structure.wlengthnc)*np.conj(np.exp(-1j*2*np.pi*self.structure.Nnc*np.cos(Th)*self.structure.thicknc/self.structure.wlengthnc)));
        self.outdata.Rs,self.outdata.Ts,Riface_s,Tiface_s,Anc_s=self.R_T_A_calc(absphi,tmmdata.Rs,tmmdata.Rsrev,tmmdata.Ts,tmmdata.Tsrev);
        self.outdata.Rp,self.outdata.Tp,Riface_p,Tiface_p,Anc_p=self.R_T_A_calc(absphi,tmmdata.Rp,tmmdata.Rprev,tmmdata.Tp,tmmdata.Tprev);
        #normalization of ploss
        if (tmmdata.plosspickup):
            self.outdata.Ps=tmmdata.Ps*Tiface_s[self.ploss_iface(),:]+tmmdata.Psrev*Riface_s[self.ploss_iface(),:];
            self.outdata.Pp=tmmdata.Pp*Tiface_p[self.ploss_iface(),:]+tmmdata.Pprev*Riface_p[self.ploss_iface(),:];
            self.outdata.P_z=tmmdata.P_z#you need to return positions too
        
        #normalization of absorption
        for ii in range(0,len(self.structure.idxcoh)):
            tmmdata.As[ii,:]=tmmdata.As[ii,:]*Tiface_s[self.structure.idxcoh[ii],:];
            tmmdata.Asrev[ii,:]=tmmdata.Asrev[ii,:]*Riface_s[self.structure.idxcoh[ii],:];
            tmmdata.Ap[ii,:]=tmmdata.Ap[ii,:]*Tiface_p[self.structure.idxcoh[ii],:];
            tmmdata.Aprev[ii,:]=tmmdata.Aprev[ii,:]*Riface_p[self.structure.idxcoh[ii],:];
        
        self.outdata.As=np.zeros(np.shape(datain.N));
        self.outdata.Ap=np.zeros(np.shape(datain.N));
        for ii in range(0,len(datain.layernames)):
            for jj in range(0,len(self.structure.namecoh)):
                if (self.structure.namecoh[jj]==datain.layernames[ii]):
                    self.outdata.As[ii,:]=self.outdata.As[ii,:]+tmmdata.As[jj,:]+tmmdata.Asrev[jj,:];
                    self.outdata.Ap[ii,:]=self.outdata.Ap[ii,:]+tmmdata.Ap[jj,:]+tmmdata.Aprev[jj,:];
            for jj in range(0,len(self.structure.namenc)):
                if (self.structure.namenc[jj]==datain.layernames[ii]):
                    self.outdata.As[ii,:]=self.outdata.As[ii,:]+Anc_s[jj,:];
                    self.outdata.Ap[ii,:]=self.outdata.Ap[ii,:]+Anc_p[jj,:];
        self.process_last_layer(datain.N)
        self.calc_average();
        return self.outdata
        
    #if last layer abosorbs absorption in last layer is set to transmission and transmission is set to zero
    def process_last_layer(self,N):
        test=np.imag(N[-1,:])!=0
        if test.any():
            self.outdata.As[-1,:]=self.outdata.Ts
            self.outdata.Ap[-1,:]=self.outdata.Tp
            self.outdata.Ts=self.outdata.Ts*0
            self.outdata.Tp=self.outdata.Tp*0
        
    def calc_average(self):
        self.outdata.Ravg=(self.outdata.Rs+self.outdata.Rp)/2;
        self.outdata.Tavg=(self.outdata.Ts+self.outdata.Tp)/2;
        self.outdata.Aavg=(self.outdata.As+self.outdata.Ap)/2;
        if self.outdata.plosspickup:
            self.outdata.Pavg=(self.outdata.Ps+self.outdata.Pp)/2;
        
    def R_T_A_calc(self,absphi,Rf,Rr,Tf,Tr):
        Tc=np.ones(np.shape(self.structure.Nnc));
        Rc=np.zeros(np.shape(self.structure.Nnc));
        Tamp=np.ones(np.shape(self.structure.Nnc));
        Anc=np.zeros(np.shape(self.structure.Nnc));
        Tiface=np.ones((np.shape(self.structure.Nnc)[0]-1,np.shape(self.structure.Nnc)[1]));
        Riface=np.zeros((np.shape(self.structure.Nnc)[0]-1,np.shape(self.structure.Nnc)[1]));
        
        for ii in range(0,np.shape(Rf)[0]):
            Rc[-2-ii,:]=Rf[-1-ii,:]+(Tf[-1-ii,:]*Tr[-1-ii,:]*Rc[-1-ii,:]*absphi[-1-ii,:]*absphi[-1-ii,:])/(1-Rr[-1-ii,:]*Rc[-1-ii,:]*absphi[-1-ii,:]*absphi[-1-ii,:]);
            Tc[-1-ii,:]=Tf[-1-ii,:]/(1-Rr[-1-ii,:]*Rc[-1-ii,:]*absphi[-1-ii,:]*absphi[-1-ii,:]);
        
        #transmision into nc layer
        for ii in range(1,np.shape(Tc)[0]):
            Tamp[ii,:]=Tamp[ii-1,:]*absphi[ii-1,:]*Tc[ii,:];
        #absorption of nc layer
        for ii in range(0,np.shape(Tc)[0]):
            Anc[ii,:]=Tamp[ii,:]*(1-absphi[ii,:])*(1+absphi[ii,:]*Rc[ii,:]);
        #transmission into coherent interface and reflection into the same coherent interface
        for ii in range(0,np.shape(Tiface)[0]):
            Tiface[ii,:]=Tamp[ii,:]*absphi[ii,:];
            Riface[ii,:]=Tamp[ii+1,:]*Rc[ii+1,:]*absphi[ii+1,:]*absphi[ii+1,:];
        return Rc[0,:],Tamp[-1,:],Riface,Tiface,Anc;
        
        
        
    def cohtmm_run(self,datain):
        #datain we only need for the input angle and for the name of the absorption layer and for the wavelegnths
        senddata=container();
        senddata.Thin=datain.Thin;
        senddata.absorption_layer=datain.absorption_layer;
        senddata.layernames=[];
        senddata.N=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
        senddata.thickness=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
        senddata.wlength=np.zeros((0,np.shape(datain.N)[1]));
        
        packdata=container();
        packdata.plosspickup=bool(0)#default value false
        packdata.As=np.zeros((0,np.shape(datain.N)[1]));
        packdata.Asrev=np.zeros((0,np.shape(datain.N)[1]));
        packdata.Ap=np.zeros((0,np.shape(datain.N)[1]));
        packdata.Aprev=np.zeros((0,np.shape(datain.N)[1]));
        packdata.Ts=np.zeros((self.structure.idxcoh[-1]+1,np.shape(datain.N)[1]));

        packdata.Tsrev=np.zeros((self.structure.idxcoh[-1]+1,np.shape(datain.N)[1]));
        packdata.Tp=np.zeros((self.structure.idxcoh[-1]+1,np.shape(datain.N)[1]));
        packdata.Tprev=np.zeros((self.structure.idxcoh[-1]+1,np.shape(datain.N)[1]));
        packdata.Rs=np.zeros((self.structure.idxcoh[-1]+1,np.shape(datain.N)[1]));
        packdata.Rsrev=np.zeros((self.structure.idxcoh[-1]+1,np.shape(datain.N)[1]));
        packdata.Rp=np.zeros((self.structure.idxcoh[-1]+1,np.shape(datain.N)[1]));
        packdata.Rprev=np.zeros((self.structure.idxcoh[-1]+1,np.shape(datain.N)[1]));
        for ii in range(self.structure.idxcoh[0],self.structure.idxcoh[-1]+1):
            for jj in range(0,len(self.structure.idxcoh)):
                if self.structure.idxcoh[jj]==ii:
                    senddata.N=np.append(senddata.N,[self.structure.Ncoh[jj]],axis=0);
                    senddata.thickness=np.append(senddata.thickness,[self.structure.thickcoh[jj]],axis=0);
                    senddata.wlength=np.append(senddata.wlength,[self.structure.wlengthcoh[jj]],axis=0);
                    senddata.layernames.append(self.structure.namecoh[jj]);
            
            
            tmpdata=cohTMM().main_calc(senddata);
            packdata.Ap=np.append(packdata.Ap,tmpdata.Ap,axis=0);
            packdata.Aprev=np.append(packdata.Aprev,tmpdata.Aprev,axis=0);
            packdata.As=np.append(packdata.As,tmpdata.As,axis=0);
            packdata.Asrev=np.append(packdata.Asrev,tmpdata.Asrev,axis=0);
            packdata.Ts[ii,:]=tmpdata.Ts;
            packdata.Tsrev[ii,:]=tmpdata.Tsrev;
            packdata.Tp[ii,:]=tmpdata.Tp;
            packdata.Tprev[ii,:]=tmpdata.Tprev;
            packdata.Rs[ii,:]=tmpdata.Rs;
            packdata.Rsrev[ii,:]=tmpdata.Rsrev;
            packdata.Rp[ii,:]=tmpdata.Rp;
            packdata.Rprev[ii,:]=tmpdata.Rprev;
            
            if tmpdata.plosspickup: #if power loss is calculated here is takeover of data
                packdata.Ps=tmpdata.Ps;
                packdata.Psrev=tmpdata.Psrev;
                packdata.Pp=tmpdata.Pp;
                packdata.Pprev=tmpdata.Pprev;
                packdata.plosspickup=tmpdata.plosspickup;
                packdata.P_z=tmpdata.P_z;
            
            senddata.layernames=[];
            senddata.N=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
            senddata.thickness=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
            senddata.wlength=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
        return packdata;
     
    def ploss_iface(self):
        for ii in range(0,len(self.structure.idxcoh)): 
            if (self.structure.namecoh[ii]==self.structure.absorption_layer):
                IDX=self.structure.idxcoh[ii];
        return IDX
    
    def process_structure(self,datain):
        interfacecnt=1;#we expect at least 1 interface with two materials (input and exit media)
        thickness=np.repeat(datain.thickness[:,np.newaxis],np.shape(datain.wlength)[1],axis=1);#input thickness is an array
        self.structure=container();
        self.structure.absorption_layer=datain.absorption_layer;
        self.structure.idxcoh=[];#it's a list
        self.structure.namecoh=[];#list
        self.structure.namenc=[];#list
        self.structure.Ncoh=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
        self.structure.thickcoh=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
        self.structure.wlengthcoh=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
        self.structure.Nnc=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
        self.structure.thicknc=np.zeros((0,np.shape(datain.N)[1]))#empty array of (0,len(wavelegnth)) dims
        self.structure.wlengthnc=np.zeros((0,np.shape(datain.N)[1]));#empty array of (0,len(wavelegnth)) dims
        #for coherent
        self.structure.idxcoh.append(interfacecnt-1);#we store 0 in the index array
        self.structure.namecoh.append(datain.layernames[0]);#storing name for the tmm
        self.structure.Ncoh=np.append(self.structure.Ncoh,[datain.N[0]],axis=0);#storing ref index for tmm
        self.structure.thickcoh=np.append(self.structure.thickcoh,[np.zeros(np.shape(datain.N)[1])],axis=0);#first layer thickness should be zero always
        self.structure.wlengthcoh=np.append(self.structure.wlengthcoh,[datain.wlength[0]],axis=0);
        
        #for noncoherent
        self.structure.namenc.append(datain.layernames[0]);#storing name for the tmm
        self.structure.Nnc=np.append(self.structure.Nnc,[datain.N[0]],axis=0);#storing ref index for tmm
        self.structure.thicknc=np.append(self.structure.thicknc,[np.zeros(np.shape(datain.N)[1])],axis=0);#first layer thickness should be zero always
        self.structure.wlengthnc=np.append(self.structure.wlengthnc,[datain.wlength[0]],axis=0);
        
        for ii in range(1,np.shape(datain.N)[0]-1):
            if (datain.layerprop[ii]=="ncoh"):
                self.structure.namenc.append(datain.layernames[ii]);#if it is ncoh store layer
                self.structure.Nnc=np.append(self.structure.Nnc,[datain.N[ii]],axis=0);#and ref index
                self.structure.thicknc=np.append(self.structure.thicknc,[thickness[ii]],axis=0);#and thickness
                self.structure.wlengthnc=np.append(self.structure.wlengthnc,[datain.wlength[ii]],axis=0);#and wavelength
                self.structure.idxcoh.append(interfacecnt-1);#for the tmm store index of interface
                self.structure.namecoh.append(datain.layernames[ii]);#layer name
                self.structure.Ncoh=np.append(self.structure.Ncoh,[datain.N[ii]],axis=0);#ref index
                self.structure.wlengthcoh=np.append(self.structure.wlengthcoh,[datain.wlength[ii]],axis=0);#wavelengths
                self.structure.thickcoh=np.append(self.structure.thickcoh,[np.zeros(np.shape(datain.N)[1])],axis=0);#last layer thickness should be zero
                interfacecnt=interfacecnt+1;#now increase index of interface
                self.structure.idxcoh.append(interfacecnt-1);#store new index of interface
                self.structure.namecoh.append(datain.layernames[ii]);#first layer name
                self.structure.Ncoh=np.append(self.structure.Ncoh,[datain.N[ii]],axis=0);#first ref index
                self.structure.wlengthcoh=np.append(self.structure.wlengthcoh,[datain.wlength[ii]],axis=0);#firest wlengths
                self.structure.thickcoh=np.append(self.structure.thickcoh,[np.zeros(np.shape(datain.N)[1])],axis=0);#first layer thickness should be zero
            else:
                self.structure.idxcoh.append(interfacecnt-1);#if it is layer for tmm store index of interface
                self.structure.namecoh.append(datain.layernames[ii]);#layername
                self.structure.Ncoh=np.append(self.structure.Ncoh,[datain.N[ii]],axis=0);#ref index
                self.structure.wlengthcoh=np.append(self.structure.wlengthcoh,[datain.wlength[ii]],axis=0);#wavelengths
                self.structure.thickcoh=np.append(self.structure.thickcoh,[thickness[ii]],axis=0);#layer thickness
        
        #exit media after the loop
        self.structure.idxcoh.append(interfacecnt-1);#last index array
        self.structure.namecoh.append(datain.layernames[-1]);#last name for the tmm
        self.structure.Ncoh=np.append(self.structure.Ncoh,[datain.N[-1]],axis=0);#last ref index for tmm
        self.structure.thickcoh=np.append(self.structure.thickcoh,[np.zeros(np.shape(datain.N)[1])],axis=0);#last layer thickness should be zero always
        self.structure.wlengthcoh=np.append(self.structure.wlengthcoh,[datain.wlength[-1]],axis=0);#last wavelength
        
        #for noncoherent
        self.structure.namenc.append(datain.layernames[-1]);#last name for the nctmm
        self.structure.Nnc=np.append(self.structure.Nnc,[datain.N[-1]],axis=0);#last ref index for nctmm
        self.structure.thicknc=np.append(self.structure.thicknc,[np.zeros(np.shape(datain.N)[1])],axis=0);#last layer thickness should be zero always
        self.structure.wlengthnc=np.append(self.structure.wlengthnc,[datain.wlength[-1]],axis=0);#last wavelegnth

        
  
#b=ncohTMM().main_calc(a)
#b=ncohTMM.main_calc(ncohTMM(),a); 
#b=cohTMM().main_calc(a);
#b=cohTMM.main_calc(cohTMM(),a);