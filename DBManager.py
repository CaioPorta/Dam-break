# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 21:46:58 2021

@author: caiop
"""
import os
from os.path import exists
import sys
import copy
import time
from datetime import datetime
from datetime import timedelta

import sqlite3
from sqlite3 import Error

class DBManager(object):
    def __init__(self, HMI):
        self.HMI = HMI

        self.conn = sqlite3.connect("Database_Dambreak.db")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Comandos ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS MacroNames ('Name' 'TEXT')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Cache ('Precisão' 'TEXT', 'Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Macro1 ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Macro2 ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Macro3 ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Macro4 ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Macro5 ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Macro6 ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Macro7 ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Macro8 ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")

        if self.GetMacroNames() == []:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO MacroNames VALUES (?)", [("Macro1")])
            cursor.execute("INSERT INTO MacroNames VALUES (?)", [("Macro2")])
            cursor.execute("INSERT INTO MacroNames VALUES (?)", [("Macro3")])
            cursor.execute("INSERT INTO MacroNames VALUES (?)", [("Macro4")])
            cursor.execute("INSERT INTO MacroNames VALUES (?)", [("Macro5")])
            cursor.execute("INSERT INTO MacroNames VALUES (?)", [("Macro6")])
            cursor.execute("INSERT INTO MacroNames VALUES (?)", [("Macro7")])
            cursor.execute("INSERT INTO MacroNames VALUES (?)", [("Macro8")])
            self.conn.commit()

    def Disconnect(self): # Só será desconectada se a FLAG estiver em FALSE, condição imposta lá na thread principal
        try: self.conn.close() # Close connection
        except: pass

    def ClearDB(self):
        self.conn.execute("DROP TABLE Comandos")
        self.conn.execute("CREATE TABLE IF NOT EXISTS Comandos ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL')")

    def WriteOnDB(self, comando):
        self.conn.execute("INSERT INTO Comandos VALUES (?,?,?,?)", [(comando[0]),comando[1],comando[2],comando[3]])
        self.conn.commit()

    def GetAllMoves(self):
        cursor = self.conn.cursor()
        retorno = []
        retorno = list(cursor.execute("SELECT * FROM Comandos"))
        return retorno

    def SetMacroName(self, macroID, Name):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE MacroNames SET Name = (?) WHERE rowid = (?)", [(Name), str(macroID+1)])
        self.conn.commit()

    def GetMacroNames(self):
        retorno = []
        retorno = list(self.conn.execute("SELECT * FROM MacroNames"))
        retorno = list(map(lambda x: x[0],retorno))
        return retorno

    def DeleteMacro(self, macroID):
        if macroID == 0: TableName = "Macro1"
        if macroID == 1: TableName = "Macro2"
        if macroID == 2: TableName = "Macro3"
        if macroID == 3: TableName = "Macro4"
        if macroID == 4: TableName = "Macro5"
        if macroID == 5: TableName = "Macro6"
        if macroID == 6: TableName = "Macro7"
        if macroID == 7: TableName = "Macro8"

        self.conn.execute("DROP TABLE "+TableName)
        self.conn.execute("CREATE TABLE IF NOT EXISTS "+TableName+" ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL')")
        cursor = self.conn.cursor()
        cursor.execute("UPDATE MacroNames SET Name = (?) WHERE rowid = (?)", [(TableName), str(macroID)])
        self.conn.commit()

    def OverwriteMacro(self, macroID, comandos):
        if macroID == 0: TableName = "Macro1"
        if macroID == 1: TableName = "Macro2"
        if macroID == 2: TableName = "Macro3"
        if macroID == 3: TableName = "Macro4"
        if macroID == 4: TableName = "Macro5"
        if macroID == 5: TableName = "Macro6"
        if macroID == 6: TableName = "Macro7"
        if macroID == 7: TableName = "Macro8"

        self.conn.execute("DROP TABLE "+TableName)
        self.conn.execute("CREATE TABLE IF NOT EXISTS "+TableName+" ('Aceleração' 'REAL', 'Velocidade' 'REAL', 'Posição' 'REAL', 'Inclinação' 'REAL', 'Atraso' 'REAL', 'Ciclos' 'INTEGER')")
        print(comandos)
        for comando in comandos:
            self.conn.execute("INSERT INTO "+TableName+" VALUES (?,?,?,?,?,?)", [(comando[0]),comando[1],comando[2],comando[3],comando[4],comando[5]])
        self.conn.commit()

    def GetMacroMoves(self, macroID):
        if macroID == 0: TableName = "Macro1"
        if macroID == 1: TableName = "Macro2"
        if macroID == 2: TableName = "Macro3"
        if macroID == 3: TableName = "Macro4"
        if macroID == 4: TableName = "Macro5"
        if macroID == 5: TableName = "Macro6"
        if macroID == 6: TableName = "Macro7"
        if macroID == 7: TableName = "Macro8"

        retorno = []
        retorno = list(self.conn.execute("SELECT * FROM "+TableName))
        return retorno

    def UpdateCache_Precisao(self, value):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Cache SET Precisão = (?)", [(value)])
        self.conn.commit()

    def UpdateCache_Aceleracao(self, value):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Cache SET Aceleração = (?)", [(value)])
        self.conn.commit()

    def UpdateCache_Velocidade(self, value):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Cache SET Velocidade = (?)", [(value)])
        self.conn.commit()

    def UpdateCache_Posicao(self, value):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Cache SET Posição = (?)", [(value)])
        self.conn.commit()

    def UpdateCache_Inclinacao(self, value):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Cache SET Inclinação = (?)", [(value)])
        self.conn.commit()

    def GetCache_Precisao(self):
        retorno = "1/32"  # Padrão
        cursor = self.conn.cursor()
        retorno = list(cursor.execute("SELECT Precisão FROM Cache"))
        if not len(retorno)>0:
            cursor.execute("INSERT INTO Cache VALUES (?,?,?,?,?)", [("1/32"),
                                                                     self.HMI.MinAceleracao,
                                                                     self.HMI.MinVelocidade,
                                                                     self.HMI.MinPosicao,
                                                                     self.HMI.MinInclinacao])
            retorno = "1/32"  # Padrão
        else:
            retorno = retorno[0][0]
        return retorno

    def GetCache_Aceleracao(self):
        cursor = self.conn.cursor()
        retorno = list(cursor.execute("SELECT Aceleração FROM Cache"))
        return retorno[0][0]

    def GetCache_Velocidade(self):
        cursor = self.conn.cursor()
        retorno = list(cursor.execute("SELECT Velocidade FROM Cache"))
        return retorno[0][0]

    def GetCache_Posicao(self):
        cursor = self.conn.cursor()
        retorno = list(cursor.execute("SELECT Posição FROM Cache"))
        return retorno[0][0]

    def GetCache_Inclinacao(self):
        cursor = self.conn.cursor()
        retorno = list(cursor.execute("SELECT Inclinação FROM Cache"))
        return retorno[0][0]