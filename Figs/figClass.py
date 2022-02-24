#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 27 17:26:21 2021

@author: tzework
"""
from matplotlib.figure import Figure

class container():
    def __init__(self):
        pass
        

class TMMfigurefull():
    def __init__(self):
        #matplotlib muliplies axes size with large figure size that is why you always divide with large figure size
        self.dim=container()
        self.dim.figwidth=18/2.54#fullfigure size
        self.dim.figheight=14/2.54#fullfigure size
        self.dim.x0=1.5/(2.54*self.dim.figwidth)#relative to large figure
        self.dim.y0=1.5/(2.54*self.dim.figwidth)#relative to large figure
        self.dim.w=7/(2.54*self.dim.figwidth)#small fig size in percentage of large figure
        self.dim.h=5/(2.54*self.dim.figheight)#small fig size in percentage of large figure
        self.dim.x1=self.dim.w+2.5*self.dim.x0
        self.dim.y1=self.dim.h+2.5*self.dim.x0
        
        self.fig=Figure()
        self.fig.set_size_inches((self.dim.figwidth,self.dim.figheight))
        self.axtl=self.fig.add_axes([self.dim.x0,self.dim.y1,self.dim.w,self.dim.h])
        self.axtl.tick_params(labelsize=8)
        self.axtl.set_xlabel('wavelength [nm]',fontsize=10, position=(0.5,0),labelpad=5)
        self.axtl.set_ylabel('Reflectance/transmittance',fontsize=10,  position=(0,0.5),labelpad=5)
        
        self.axtr=self.fig.add_axes([self.dim.x1,self.dim.y1,self.dim.w,self.dim.h])
        self.axtr.tick_params(labelsize=8)
        self.axtr.set_xlabel('Position [nm]',fontsize=10, position=(0.5,0),labelpad=5)
        self.axtr.set_ylabel(r'G(z) [m$^{-3}$s$^{-1}$]',fontsize=10,  position=(0,0.5),labelpad=5)
         
        self.axbl=self.fig.add_axes([self.dim.x0,self.dim.y0,self.dim.w,self.dim.h])
        self.axbl.tick_params(labelsize=8)
        self.axbl.set_xlabel('wavelength [nm]',fontsize=10, position=(0.5,0),labelpad=5)
        self.axbl.set_ylabel('Absorption in layers',fontsize=10,  position=(0,0.5),labelpad=5)
        
        self.axbr=self.fig.add_axes([self.dim.x1,self.dim.y0,self.dim.w,self.dim.h])
        self.axbr.tick_params(labelsize=8)
        self.axbr.set_xlabel('Position [nm]',fontsize=10, position=(0.5,0),labelpad=5)
        self.axbr.set_ylabel(r'G(z,$\lambda$)  [m$^{-3}$s$^{-1}$]',fontsize=10,  position=(0,0.5),labelpad=5)
        
class TMMfigure():
    def __init__(self):
        #matplotlib muliplies axes size with large figure size that is why you always divide with large figure size
        self.dim=container()
        self.dim.figwidth=9.5/2.54#fullfigure size
        self.dim.figheight=14/2.54#fullfigure size
        self.dim.x0=1.5/(2.54*self.dim.figwidth)#relative to large figure
        self.dim.y0=0.75/(2.54*self.dim.figwidth)#relative to large figure
        self.dim.w=7/(2.54*self.dim.figwidth)#small fig size in percentage of large figure
        self.dim.h=5/(2.54*self.dim.figheight)#small fig size in percentage of large figure
        self.dim.x1=self.dim.w+2.5*self.dim.x0
        self.dim.y1=self.dim.h+2.5*self.dim.y0
        
        self.fig=Figure()
        self.fig.set_size_inches((self.dim.figwidth,self.dim.figheight))
        self.axtl=self.fig.add_axes([self.dim.x0,self.dim.y1,self.dim.w,self.dim.h])
        self.axtl.tick_params(labelsize=8)
        self.axtl.set_xlabel('wavelength [nm]',fontsize=10, position=(0.5,0),labelpad=5)
        self.axtl.set_ylabel('Reflectance/transmittance',fontsize=10,  position=(0,0.5),labelpad=5)
        
         
        self.axbl=self.fig.add_axes([self.dim.x0,self.dim.y0,self.dim.w,self.dim.h])
        self.axbl.tick_params(labelsize=8)
        self.axbl.set_xlabel('wavelength [nm]',fontsize=10, position=(0.5,0),labelpad=5)
        self.axbl.set_ylabel('Absorption in layers',fontsize=10,  position=(0,0.5),labelpad=5)
        

