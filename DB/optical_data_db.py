#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  3 20:09:46 2021

@author: tzework
"""
import sqlite3

class container():
    pass

class ODB_class():
    def __init__(self):
        pass
    def make_connection(self,DBname):
        try:
            conn = sqlite3.connect(DBname)
            errormsg=''
        except conn.Error as e:
            errormsg=e  
        return conn,errormsg
    
    def Get_tables(self,conn):
        cursor=conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables=[v[0] for v in cursor.fetchall() if v[0] != "sqlite_sequence"]
        return tables
    
    def table_test(self,conn):
        tables=self.Get_tables(conn)
        if tables != ['Materials', 'Optical_Data']:
            errormsg='Wrong data\nbase is opened.'
        else:
            errormsg=''
        return errormsg
    
    def overwrite_DB(self,conn):
        cursor=conn.cursor()
        tables=self.Get_tables(conn)
        if tables!=[]:
            for table in tables:
                sqlcmd='DROP table '+table
                cursor.execute(sqlcmd)
                conn.commit()
                
    def create_DB(self,conn):
        self.overwrite_DB(conn)
        cursor=conn.cursor()
        sqlcmd="""CREATE TABLE Materials (
        Name TEXT NOT NULL,
        wlength_min REAL,
        wlength_max REAL,
        wlength_Num INTEGER,
        wlength_unit TEXT,
        Mat_ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
        )"""
        cursor.execute(sqlcmd)
        conn.commit()
        sqlcmd="""CREATE TABLE Optical_Data (
        wlength REAL NOT NULL,
        n	REAL NOT NULL,
        k	REAL NOT NULL,
        Mat_ID INTEGER,
        Entry_ID	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        FOREIGN KEY (Mat_ID) REFERENCES Materials (Mat_ID) ON UPDATE CASCADE ON DELETE CASCADE
        )"""
        cursor.execute(sqlcmd)
        conn.commit()
    
    def get_materials(self,conn):
        cursor=conn.cursor()
        sqlcmd='''SELECT Name, wlength_min, wlength_max, wlength_unit, wlength_Num, mat_ID FROM Materials'''
        cursor.execute(sqlcmd)
        data=cursor.fetchall()
        return data

#next function automatically disregards data where wavelegnth units are not in meters this is not needed anymore since I solved the isue in TMM app
    def get_valid_materials(self,conn):
        cursor=conn.cursor()
        sqlcmd='''SELECT Name, wlength_min, wlength_max, wlength_unit, wlength_Num, mat_ID FROM Materials WHERE wlength_unit=?'''
        cursor.execute(sqlcmd,('m',))
        data=cursor.fetchall()
        return data
    
    def get_data(self,conn,mat_id):
        cursor=conn.cursor()
        sqlcmd='''SELECT wlength, n, k FROM Optical_Data Where Mat_ID=?'''
        cursor.execute(sqlcmd,(mat_id,))
        return cursor.fetchall()
    
    def insert_into_data(self,conn,optdata,mat_id):
        cursor=conn.cursor()
        sqlcmd = ''' INSERT INTO Optical_Data (wlength,n,k,Mat_ID) 
        VALUES(?,?,?,?) '''
        for line in optdata:
            data_to_insert=(line[0],line[1],line[2],mat_id)
            cursor.execute(sqlcmd,data_to_insert)
            conn.commit()
    
    def check_if_material_exists(self,conn,data_to_check):
        cursor=conn.cursor()
        sqlcmd='''SELECT Name,wlength_min,wlength_max,wlength_unit,wlength_Num FROM Materials WHERE Name=?'''
        cursor.execute(sqlcmd,(data_to_check[0],))
        data=cursor.fetchall()
        if data==[data_to_check]:
            errormsg="Data in file is\nalready in database."
        else:
            errormsg=''
        return errormsg
    
    def insert_into_materials(self,conn,data_to_insert):
        errormsg=self.check_if_material_exists(conn,data_to_insert)
        mat_id='NaN'
        if errormsg=='':
            cursor=conn.cursor()
            sqlcmd = ''' INSERT INTO Materials (Name,wlength_min,wlength_max,wlength_unit,wlength_Num) 
        VALUES(?,?,?,?,?) '''
            cursor.execute(sqlcmd,data_to_insert)
            conn.commit()
            mat_id=cursor.lastrowid
        return errormsg,mat_id
    
    def delete_from_materials(self,conn,mat_id):
        cursor=conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        sqlcmd = ''' DELETE FROM Materials WHERE Mat_ID=? '''
        cursor.execute(sqlcmd, (mat_id,))
        conn.commit()
        