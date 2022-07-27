# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 15:49:21 2021
@author: CaioPorta

Feito para Professor Geraldo de Freitas Maciel
UNESP - FEIS
"""
# This is the Main file. You may run this file.
#%% Initiate HMI
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from time import sleep

import os
import sys
import ctypes
import csv

import sys
import glob
import serial

import tkinter
from tkinter import filedialog

from DBManager import DBManager
from ArduinoComm import ArduinoComm
from WorkerThread import WorkerThread

class IHMmain(QWidget):
    def __init__(self):
        self.APPVersion = "Controle de Dambreak\nVersão Alpha 0.0.1\nÚltima modificação: 03/12/2021"
        super().__init__()
        self.setObjectName("IHM")

        self.DBManager = DBManager(self)
        self.ArduinoComm = ArduinoComm(self)

        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.screen_height = screensize[1] # FHD
        self.screen_width = screensize[0] # FHD
        self.font8 = QFont('Times New Roman', 8)
        self.font8.setBold(False)
        self.font9 = QFont('Times New Roman', 9)
        self.font9.setBold(False)
        self.font10 = QFont('Times New Roman', 10)
        self.font10.setBold(False)
        self.font12 = QFont('Times New Roman', 12)
        self.font12.setBold(False)
        self.font14 = QFont('Times New Roman', 14)
        self.font16 = QFont('Times New Roman', 16)
        self.font18 = QFont('Times New Roman', 18)
        self.font20 = QFont('Times New Roman', 20, QFont.Bold)
        self.font22 = QFont('Times New Roman', 22, QFont.Bold)
        self.font24 = QFont('Times New Roman', 24)
        self.font26 = QFont('Cooper Black', 26, QFont.Bold)
        self.font28 = QFont('Cooper Black', 28, QFont.Bold)
        self.font30 = QFont('Cooper Black', 30, QFont.Bold)

        self.setWindowTitle("Dambreak")
        self.setWindowIcon(QIcon(".\images\Dambreak IHM icon.png"))
        self.setAutoFillBackground(True)
        self.setMinimumSize(QSize(int(self.screen_width*0.55), int(self.screen_height*0.75)))
        self.showMaximized()

        self.installEventFilter(self)

        # Variáveis iniciais
        self.backgroundStyle = 'Bright'
        self.GravarMacro = "normal" # Faz App iniciar na pagina inicial
        self.MaxAceleracao = 1. # (mm/s²)
        self.MinAceleracao = 0. # (mm/s²)
        self.MaxVelocidade = 10. # (mm/s)
        self.MinVelocidade = 0. # (mm/s)
        self.MaxPosicao = 300. # (mm)
        self.MinPosicao = 0. # (mm)
        self.MaxInclinacao = 20. # (°)
        self.MinInclinacao = 0. # (°)

        self.Precisao = self.DBManager.GetCache_Precisao()
        self.Aceleracao = self.DBManager.GetCache_Aceleracao()
        self.Velocidade = self.DBManager.GetCache_Velocidade()
        self.Posicao = self.DBManager.GetCache_Posicao()
        self.Inclinacao = self.DBManager.GetCache_Inclinacao()

        self.PrecisaoAceleracao = 0.1 # (mm/s²)
        self.PrecisaoVelocidade = 0.1 # (mm/s)
        self.PrecisaoPosicao = 0.1 # (mm)
        self.PrecisaoInclinacao = 0.5 # (°)

        self.Senha = "0000"
        self.MacroRunning = False
        self.filedialogIsOpen = False
        
        self.ArduinoComm.Connect(self.DBManager.GetCache_Port())

        # Criar Página HMI
        self.GLayout = QGridLayout()
        self.setLayout(self.GLayout)

        self.CreatePageMain()

    def CreatePageMain(self):
        #%% Gestão do tema
        if self.backgroundStyle == 'Dark':
            BackgroundColor = 'black'
            BackgroundColor2 = 'gray'
            FontColor = 'white'
        else:
            BackgroundColor = 'gray'
            BackgroundColor2 = 'white'
            FontColor = 'black'
        background = self.palette()
        background.setColor(self.backgroundRole(), QColor(BackgroundColor))
        self.setPalette(background)

        self.Background_1 = QLabel()
        self.Background_1.setStyleSheet("background-color: "+BackgroundColor)

        #%% Gestão dos widgets (Label, Button, LineEdit, Table)
        self.Label_Titulo = QLabel()
        self.Label_Titulo.setAlignment(Qt.AlignCenter)
        self.Label_Titulo.setText('Controle de Dambreak')
        self.Label_Titulo.setStyleSheet('color: '+FontColor)
        self.Label_Titulo.setFont(self.font30)
        self.Label_Titulo.setFixedHeight(int(self.screen_height/20))

        self.Label_1 = QLabel()
        self.Label_1.setAlignment(Qt.AlignCenter)
        self.Label_1.setText('Macros')
        self.Label_1.setStyleSheet('color: '+FontColor)
        self.Label_1.setFont(self.font24)

        self.Label_2 = QLabel()
        self.Label_2.setAlignment(Qt.AlignCenter)
        self.Label_2.setText('Comandos manuais')
        self.Label_2.setStyleSheet('color: '+FontColor)
        self.Label_2.setFont(self.font24)

        self.Label_3 = QLabel()
        self.Label_3.setAlignment(Qt.AlignCenter)
        self.Label_3.setText('Status')
        self.Label_3.setStyleSheet('color: '+FontColor)
        self.Label_3.setFont(self.font24)

        self.Label_4 = QLabel()
        self.Label_4.setAlignment(Qt.AlignCenter)
        self.Label_4.setText('Aceleração máx')
        self.Label_4.setStyleSheet('color: '+FontColor)
        self.Label_4.setFont(self.font16)

        self.Label_5 = QLabel()
        self.Label_5.setAlignment(Qt.AlignCenter)
        self.Label_5.setText('Valocidade máx')
        self.Label_5.setStyleSheet('color: '+FontColor)
        self.Label_5.setFont(self.font16)

        self.Label_6 = QLabel()
        self.Label_6.setAlignment(Qt.AlignCenter)
        self.Label_6.setText('Ir para posição')
        self.Label_6.setStyleSheet('color: '+FontColor)
        self.Label_6.setFont(self.font16)

        self.Label_7 = QLabel()
        self.Label_7.setAlignment(Qt.AlignCenter)
        self.Label_7.setText('Ir para inclinação')
        self.Label_7.setStyleSheet('color: '+FontColor)
        self.Label_7.setFont(self.font16)

        self.Label_8 = QLabel()
        self.Label_8.setAlignment(Qt.AlignCenter)
        self.Label_8.setText('Posição atual\n'+str(self.Posicao)+'mm')
        self.Label_8.setStyleSheet('color: '+FontColor)
        self.Label_8.setFont(self.font16)

        self.Label_9 = QLabel()
        self.Label_9.setAlignment(Qt.AlignCenter)
        self.Label_9.setText('Inclinação atual\n'+str(self.Inclinacao)+'°')
        self.Label_9.setStyleSheet('color: '+FontColor)
        self.Label_9.setFont(self.font16)

        self.Label_10 = QLabel('')
        self.Label_10.setFixedHeight(int(self.screen_height/30))

        self.Label_11 = QLabel('')
        self.Label_11.setFixedHeight(int(self.screen_height/30))

        self.Label_12 = QLabel()
        self.Label_12.setAlignment(Qt.AlignCenter)
        self.Label_12.setText('Histórico de comandos')
        self.Label_12.setStyleSheet('color: '+FontColor)
        self.Label_12.setFont(self.font16)

        self.Label_13 = QLabel()
        self.Label_13.setAlignment(Qt.AlignCenter)
        self.Label_13.setText('Precisão')
        self.Label_13.setStyleSheet('color: '+FontColor)
        self.Label_13.setFont(self.font16)

        self.Button_Tema = QPushButton()
        self.Button_Tema.setFixedWidth(int(self.screen_width/15))
        self.Button_Tema.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Tema.setStyleSheet("background-color: "+BackgroundColor+"; border: none; outline: none;")
        self.Button_Tema.pressed.connect(lambda: self.OnButtonPressed('Mudar tema'))
        self.Button_Tema.setIconSize(QSize(int(self.frameGeometry().height()/15),int(self.frameGeometry().height()/15)))
        self.Button_Tema.setIcon(QIcon("./images/Dambreak IHM icon.png"))

        MacroNames = self.DBManager.GetMacroNames()
        self.Button_Macro1 = QPushButton(MacroNames[0])
        self.Button_Macro1.setFont(self.font18)
        self.Button_Macro1.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
        self.Button_Macro1.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Macro1.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_Macro1.pressed.connect(lambda: self.OnButtonPressed('Macro1'))

        self.Button_Macro2 = QPushButton(MacroNames[1])
        self.Button_Macro2.setFont(self.font18)
        self.Button_Macro2.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
        self.Button_Macro2.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Macro2.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_Macro2.pressed.connect(lambda: self.OnButtonPressed('Macro2'))

        self.Button_Macro3 = QPushButton(MacroNames[2])
        self.Button_Macro3.setFont(self.font18)
        self.Button_Macro3.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
        self.Button_Macro3.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Macro3.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_Macro3.pressed.connect(lambda: self.OnButtonPressed('Macro3'))

        self.Button_Macro4 = QPushButton(MacroNames[3])
        self.Button_Macro4.setFont(self.font18)
        self.Button_Macro4.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
        self.Button_Macro4.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Macro4.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_Macro4.pressed.connect(lambda: self.OnButtonPressed('Macro4'))

        self.Button_Macro5 = QPushButton(MacroNames[4])
        self.Button_Macro5.setFont(self.font18)
        self.Button_Macro5.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
        self.Button_Macro5.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Macro5.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_Macro5.pressed.connect(lambda: self.OnButtonPressed('Macro5'))

        self.Button_Macro6 = QPushButton(MacroNames[5])
        self.Button_Macro6.setFont(self.font18)
        self.Button_Macro6.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
        self.Button_Macro6.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Macro6.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_Macro6.pressed.connect(lambda: self.OnButtonPressed('Macro6'))

        self.Button_Macro7 = QPushButton(MacroNames[6])
        self.Button_Macro7.setFont(self.font18)
        self.Button_Macro7.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
        self.Button_Macro7.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Macro7.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_Macro7.pressed.connect(lambda: self.OnButtonPressed('Macro7'))

        self.Button_Macro8 = QPushButton(MacroNames[7])
        self.Button_Macro8.setFont(self.font18)
        self.Button_Macro8.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
        self.Button_Macro8.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Macro8.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_Macro8.pressed.connect(lambda: self.OnButtonPressed('Macro8'))

        self.Button_GravarMacro = QPushButton('Editar\nmacros')
        self.Button_GravarMacro.setFont(self.font24)
        self.Button_GravarMacro.adjustSize()
        self.Button_GravarMacro.setFixedWidth(int(self.frameGeometry().width()/7))
        self.Button_GravarMacro.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_GravarMacro.setStyleSheet("background-color: "+BackgroundColor2+";border: none; outline: none;")
        self.Button_GravarMacro.pressed.connect(lambda: self.OnButtonPressed('GravarMacro'))

        self.Button_DeletarMacro = QPushButton('Deletar\nmacros')
        self.Button_DeletarMacro.setFont(self.font24)
        self.Button_DeletarMacro.adjustSize()
        self.Button_DeletarMacro.setFixedWidth(int(self.frameGeometry().width()/7))
        self.Button_DeletarMacro.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_DeletarMacro.setStyleSheet("background-color: "+BackgroundColor2+"; color:border: none; outline: none;")
        self.Button_DeletarMacro.pressed.connect(lambda: self.OnButtonPressed('DeletarMacro'))

        self.Button_MaisAceleracao = QPushButton('+')
        self.Button_MaisAceleracao.setFont(self.font14)
        self.Button_MaisAceleracao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MaisAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MaisAceleracao.pressed.connect(lambda: self.OnButtonPressed('MaisAceleracao'))
        self.Button_MaisAceleracao.released.connect(lambda: self.OnButtonReleased('MaisAceleracao'))
        self.Button_MaisAceleracao.setFixedWidth(int(self.frameGeometry().width()/20))

        self.Button_MenosAceleracao = QPushButton('-')
        self.Button_MenosAceleracao.setFont(self.font14)
        self.Button_MenosAceleracao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MenosAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MenosAceleracao.pressed.connect(lambda: self.OnButtonPressed('MenosAceleracao'))
        self.Button_MenosAceleracao.released.connect(lambda: self.OnButtonReleased('MenosAceleracao'))
        self.Button_MenosAceleracao.setFixedWidth(int(self.frameGeometry().width()/20))

        self.Button_MaisVelocidade = QPushButton('+')
        self.Button_MaisVelocidade.setFont(self.font14)
        self.Button_MaisVelocidade.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MaisVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MaisVelocidade.pressed.connect(lambda: self.OnButtonPressed('MaisVelocidade'))
        self.Button_MaisVelocidade.released.connect(lambda: self.OnButtonReleased('MaisVelocidade'))
        self.Button_MaisVelocidade.setFixedWidth(int(self.frameGeometry().width()/20))

        self.Button_MenosVelocidade = QPushButton('-')
        self.Button_MenosVelocidade.setFont(self.font14)
        self.Button_MenosVelocidade.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MenosVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MenosVelocidade.pressed.connect(lambda: self.OnButtonPressed('MenosVelocidade'))
        self.Button_MenosVelocidade.released.connect(lambda: self.OnButtonReleased('MenosVelocidade'))
        self.Button_MenosVelocidade.setFixedWidth(int(self.frameGeometry().width()/20))

        self.Button_MaisPosicao = QPushButton('+')
        self.Button_MaisPosicao.setFont(self.font14)
        self.Button_MaisPosicao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MaisPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MaisPosicao.pressed.connect(lambda: self.OnButtonPressed('MaisPosicao'))
        self.Button_MaisPosicao.released.connect(lambda: self.OnButtonReleased('MaisPosicao'))
        self.Button_MaisPosicao.setFixedWidth(int(self.frameGeometry().width()/20))

        self.Button_MenosPosicao = QPushButton('-')
        self.Button_MenosPosicao.setFont(self.font14)
        self.Button_MenosPosicao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MenosPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MenosPosicao.pressed.connect(lambda: self.OnButtonPressed('MenosPosicao'))
        self.Button_MenosPosicao.released.connect(lambda: self.OnButtonReleased('MenosPosicao'))
        self.Button_MenosPosicao.setFixedWidth(int(self.frameGeometry().width()/20))

        self.Button_MaisInclinacao = QPushButton('+')
        self.Button_MaisInclinacao.setFont(self.font14)
        self.Button_MaisInclinacao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MaisInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MaisInclinacao.pressed.connect(lambda: self.OnButtonPressed('MaisInclinacao'))
        self.Button_MaisInclinacao.released.connect(lambda: self.OnButtonReleased('MaisInclinacao'))
        self.Button_MaisInclinacao.setFixedWidth(int(self.frameGeometry().width()/20))

        self.Button_MenosInclinacao = QPushButton('-')
        self.Button_MenosInclinacao.setFont(self.font14)
        self.Button_MenosInclinacao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MenosInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MenosInclinacao.pressed.connect(lambda: self.OnButtonPressed('MenosInclinacao'))
        self.Button_MenosInclinacao.released.connect(lambda: self.OnButtonReleased('MenosInclinacao'))
        self.Button_MenosInclinacao.setFixedWidth(int(self.frameGeometry().width()/20))

        self.Button_MaxAceleracao = QPushButton('Max')
        self.Button_MaxAceleracao.setFont(self.font14)
        self.Button_MaxAceleracao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MaxAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MaxAceleracao.pressed.connect(lambda: self.OnButtonPressed('MaxAceleracao'))
        self.Button_MaxAceleracao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MedAceleracao = QPushButton('Med')
        self.Button_MedAceleracao.setFont(self.font14)
        self.Button_MedAceleracao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MedAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MedAceleracao.pressed.connect(lambda: self.OnButtonPressed('MedAceleracao'))
        self.Button_MedAceleracao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MinAceleracao = QPushButton('Min')
        self.Button_MinAceleracao.setFont(self.font14)
        self.Button_MinAceleracao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MinAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MinAceleracao.pressed.connect(lambda: self.OnButtonPressed('MinAceleracao'))
        self.Button_MinAceleracao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MaxVelocidade = QPushButton('Max')
        self.Button_MaxVelocidade.setFont(self.font14)
        self.Button_MaxVelocidade.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MaxVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MaxVelocidade.pressed.connect(lambda: self.OnButtonPressed('MaxVelocidade'))
        self.Button_MaxVelocidade.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MedVelocidade = QPushButton('Med')
        self.Button_MedVelocidade.setFont(self.font14)
        self.Button_MedVelocidade.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MedVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MedVelocidade.pressed.connect(lambda: self.OnButtonPressed('MedVelocidade'))
        self.Button_MedVelocidade.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MinVelocidade = QPushButton('Min')
        self.Button_MinVelocidade.setFont(self.font14)
        self.Button_MinVelocidade.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MinVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MinVelocidade.pressed.connect(lambda: self.OnButtonPressed('MinVelocidade'))
        self.Button_MinVelocidade.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MaxPosicao = QPushButton('Max')
        self.Button_MaxPosicao.setFont(self.font14)
        self.Button_MaxPosicao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MaxPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MaxPosicao.pressed.connect(lambda: self.OnButtonPressed('MaxPosicao'))
        self.Button_MaxPosicao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MedPosicao = QPushButton('Med')
        self.Button_MedPosicao.setFont(self.font14)
        self.Button_MedPosicao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MedPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MedPosicao.pressed.connect(lambda: self.OnButtonPressed('MedPosicao'))
        self.Button_MedPosicao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MinPosicao = QPushButton('Min')
        self.Button_MinPosicao.setFont(self.font14)
        self.Button_MinPosicao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MinPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MinPosicao.pressed.connect(lambda: self.OnButtonPressed('MinPosicao'))
        self.Button_MinPosicao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MaxInclinacao = QPushButton('Max')
        self.Button_MaxInclinacao.setFont(self.font14)
        self.Button_MaxInclinacao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MaxInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MaxInclinacao.pressed.connect(lambda: self.OnButtonPressed('MaxInclinacao'))
        self.Button_MaxInclinacao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MedInclinacao = QPushButton('Med')
        self.Button_MedInclinacao.setFont(self.font14)
        self.Button_MedInclinacao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MedInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MedInclinacao.pressed.connect(lambda: self.OnButtonPressed('MedInclinacao'))
        self.Button_MedInclinacao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_MinInclinacao = QPushButton('Min')
        self.Button_MinInclinacao.setFont(self.font14)
        self.Button_MinInclinacao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_MinInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_MinInclinacao.pressed.connect(lambda: self.OnButtonPressed('MinInclinacao'))
        self.Button_MinInclinacao.setFixedWidth(int(self.frameGeometry().width()/15))

        self.Button_Executar = QPushButton('Executar\ncomando')
        self.Button_Executar.setFixedWidth(int(self.frameGeometry().width()/3))
        self.Button_Executar.setFixedHeight(int(self.screen_height/10))
        self.Button_Executar.setFont(self.font22)
        self.Button_Executar.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_Executar.setStyleSheet("background-color: green; border: none; outline: none;")
        self.Button_Executar.pressed.connect(lambda: self.OnButtonPressed('Executar'))

        self.Button_LimparDB = QPushButton()
        self.Button_LimparDB.setFixedWidth(int(self.screen_width/15))
        self.Button_LimparDB.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_LimparDB.setStyleSheet("background-color: "+BackgroundColor+"; border: none; outline: none;")
        self.Button_LimparDB.pressed.connect(lambda: self.OnButtonPressed('LimparDB'))
        self.Button_LimparDB.setIconSize(QSize(int(self.frameGeometry().height()/20),int(self.frameGeometry().height()/20)))
        self.Button_LimparDB.setIcon(QIcon("./images/Limpar DB.png"))

        self.Button_DeletarAcao = QPushButton('Deletar\núltima ação')
        self.Button_DeletarAcao.setFixedWidth(int(self.frameGeometry().width()/7))
        self.Button_DeletarAcao.setFont(self.font22)
        self.Button_DeletarAcao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_DeletarAcao.setStyleSheet("background-color: red; border: none; outline: none;")
        self.Button_DeletarAcao.pressed.connect(lambda: self.OnButtonPressed('DeletarAcao'))

        self.Button_RegistrarAcao = QPushButton('Registrar\núltima ação')
        self.Button_RegistrarAcao.setFixedWidth(int(self.frameGeometry().width()/7))
        self.Button_RegistrarAcao.setFont(self.font22)
        self.Button_RegistrarAcao.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_RegistrarAcao.setStyleSheet("background-color: green; border: none; outline: none;")
        self.Button_RegistrarAcao.pressed.connect(lambda: self.OnButtonPressed('RegistrarAcao'))

        self.Button_TestarMacro = QPushButton('Testar\nmacro')
        self.Button_TestarMacro.setFixedWidth(int(self.frameGeometry().width()/7))
        self.Button_TestarMacro.setFont(self.font22)
        self.Button_TestarMacro.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_TestarMacro.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_TestarMacro.pressed.connect(lambda: self.OnButtonPressed('TestarMacro'))

        self.Button_RegistrarMacro = QPushButton('Gravar\nmacro')
        self.Button_RegistrarMacro.setFixedWidth(int(self.frameGeometry().width()/7))
        self.Button_RegistrarMacro.setFont(self.font22)
        self.Button_RegistrarMacro.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_RegistrarMacro.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_RegistrarMacro.pressed.connect(lambda: self.OnButtonPressed('RegistrarMacro'))

        self.Button_CancelarMacro = QPushButton('Cancelar\ngravação')
        self.Button_CancelarMacro.setFixedWidth(int(self.frameGeometry().width()/7))
        self.Button_CancelarMacro.setFont(self.font22)
        self.Button_CancelarMacro.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_CancelarMacro.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.Button_CancelarMacro.pressed.connect(lambda: self.OnButtonPressed('CancelarMacro'))

        self.Button_VersionInfo = QPushButton()
        self.Button_VersionInfo.pressed.connect(lambda: QMessageBox.about(self,'Informações da versão do APP', self.APPVersion))
        self.Button_VersionInfo.setIcon(QIcon("./images/Info.png"))
        self.Button_VersionInfo.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_VersionInfo.setStyleSheet("background-color: none; border: none; outline: none;")

        self.Button_ArduinoConnect = QPushButton()
        self.Button_ArduinoConnect.pressed.connect(lambda: self.OnButtonPressed('ArduinoConnect'))
        self.Button_ArduinoConnect.setIcon(QIcon("./images/arduino-logo.png"))
        self.Button_ArduinoConnect.setCursor(QCursor(Qt.PointingHandCursor))
        self.Button_ArduinoConnect.setStyleSheet("background-color: none; border: none; outline: none;")

        self.TextBox_Aceleracao = QLineEdit(str(self.Aceleracao))
        self.TextBox_Aceleracao.setFont(self.font12)
        self.TextBox_Aceleracao.setEnabled(False)
        self.TextBox_Aceleracao.setFixedWidth(int(self.frameGeometry().width()/10))
        self.TextBox_Aceleracao.setInputMask("99.9mm/s²")
        self.TextBox_Aceleracao.setAlignment(Qt.AlignRight)
        self.TextBox_Aceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; color: black; border: none; outline: none;")
        self.TextBox_Aceleracao.textChanged[str].connect(self.OnValueChanged_Aceleracao)

        self.TextBox_Velocidade = QLineEdit(str(self.Velocidade))
        self.TextBox_Velocidade.setFont(self.font12)
        self.TextBox_Velocidade.setEnabled(False)
        self.TextBox_Velocidade.setFixedWidth(int(self.frameGeometry().width()/10))
        self.TextBox_Velocidade.setInputMask("99.9mm/s")
        self.TextBox_Velocidade.setAlignment(Qt.AlignRight)
        self.TextBox_Velocidade.setStyleSheet("background-color: "+BackgroundColor2+"; color: black; border: none; outline: none;")
        self.TextBox_Velocidade.textChanged[str].connect(self.OnValueChanged_Velocidade)

        self.TextBox_Posicao = QLineEdit(str(self.Posicao))
        self.TextBox_Posicao.setFont(self.font12)
        self.TextBox_Posicao.setEnabled(False)
        self.TextBox_Posicao.setFixedWidth(int(self.frameGeometry().width()/10))
        self.TextBox_Posicao.setInputMask("999.9mm")
        self.TextBox_Posicao.setAlignment(Qt.AlignRight)
        self.TextBox_Posicao.setStyleSheet("background-color: "+BackgroundColor2+"; color: black; border: none; outline: none;")
        self.TextBox_Posicao.textChanged[str].connect(self.OnValueChanged_Posicao)

        self.TextBox_Inclinacao = QLineEdit(str(self.Inclinacao))
        self.TextBox_Inclinacao.setFont(self.font12)
        self.TextBox_Inclinacao.setEnabled(False)
        self.TextBox_Inclinacao.setFixedWidth(int(self.frameGeometry().width()/10))
        self.TextBox_Inclinacao.setInputMask("99.9°")
        self.TextBox_Inclinacao.setAlignment(Qt.AlignRight)
        self.TextBox_Inclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; color: black; border: none; outline: none;")
        self.TextBox_Inclinacao.textChanged[str].connect(self.OnValueChanged_Inclinacao)

        self.TextBox_Ciclos = QLineEdit("1")
        self.TextBox_Ciclos.setFont(self.font14)
        self.TextBox_Ciclos.setFixedWidth(int(self.frameGeometry().width()/7))
        self.TextBox_Ciclos.setInputMask("99 ciclos")
        self.TextBox_Ciclos.setAlignment(Qt.AlignRight)
        self.TextBox_Ciclos.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.TextBox_Ciclos.textChanged[str].connect(self.OnValueChanged_Ciclos)

        self.Checkbox_Precisao1 = QRadioButton("1")
        self.Checkbox_Precisao1.toggled.connect(lambda:self.Checkbox_ChangedState("1"))

        self.Checkbox_Precisao2 = QRadioButton("1/2")
        self.Checkbox_Precisao2.toggled.connect(lambda:self.Checkbox_ChangedState("1/2"))

        self.Checkbox_Precisao3 = QRadioButton("1/4")
        self.Checkbox_Precisao3.toggled.connect(lambda:self.Checkbox_ChangedState("1/4"))

        self.Checkbox_Precisao4 = QRadioButton("1/8")
        self.Checkbox_Precisao4.toggled.connect(lambda:self.Checkbox_ChangedState("1/8"))

        self.Checkbox_Precisao5 = QRadioButton("1/16")
        self.Checkbox_Precisao5.toggled.connect(lambda:self.Checkbox_ChangedState("1/16"))

        self.Checkbox_Precisao6 = QRadioButton("1/32")
        self.Checkbox_Precisao6.toggled.connect(lambda:self.Checkbox_ChangedState("1/32"))

        self.GroupCheckbox_Precisao = QButtonGroup()
        self.GroupCheckbox_Precisao.addButton(self.Checkbox_Precisao1)
        self.GroupCheckbox_Precisao.addButton(self.Checkbox_Precisao2)
        self.GroupCheckbox_Precisao.addButton(self.Checkbox_Precisao3)
        self.GroupCheckbox_Precisao.addButton(self.Checkbox_Precisao4)
        self.GroupCheckbox_Precisao.addButton(self.Checkbox_Precisao5)
        self.GroupCheckbox_Precisao.addButton(self.Checkbox_Precisao6)

        if self.Precisao == "1": self.Checkbox_Precisao1.setChecked(True)
        elif self.Precisao == "1/2": self.Checkbox_Precisao2.setChecked(True)
        elif self.Precisao == "1/4": self.Checkbox_Precisao3.setChecked(True)
        elif self.Precisao == "1/8": self.Checkbox_Precisao4.setChecked(True)
        elif self.Precisao == "1/16": self.Checkbox_Precisao5.setChecked(True)
        elif self.Precisao == "1/32": self.Checkbox_Precisao6.setChecked(True)

        self.ComboBox_Macros = QComboBox()
        self.ComboBox_Macros.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.ComboBox_Macros.setFixedWidth(int(self.frameGeometry().width()*2/7))
        self.edit = QLineEdit(self)
        self.edit.setFont(self.font16)
        self.edit.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
        self.edit.setAlignment(Qt.AlignCenter)
        self.edit.returnPressed.connect(lambda: self.OnButtonPressed('ComboBox_Macros'))
        self.ComboBox_Macros.setLineEdit(self.edit)
        self.ComboBox_Macros.setFont(self.font16)
        self.ComboBox_Macros.setCursor(QCursor(Qt.PointingHandCursor))
        for MacroName in self.DBManager.GetMacroNames():
            self.ComboBox_Macros.addItem(MacroName)

        def DefinirGeometria_Table_Historico():
            self.Table_Historico.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            self.Table_Historico.setFixedWidth(int(self.frameGeometry().width()*0.3))
            self.Table_Historico.setShowGrid(False)
            self.Table_Historico.verticalHeader().hide()
            self.Table_Historico.horizontalHeader().hide()
            self.Table_Historico.setFont(self.font10)
            self.Table_Historico.setColumnCount(1)

        self.Table_Historico = QTableWidget()
        DefinirGeometria_Table_Historico()
        self.InsertDataInTable_Historio()

        def DefinirGeometria_Table_Macro():
            self.Table_Macro.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            self.Table_Macro.setFixedWidth(int(self.frameGeometry().width()*2/7))
            self.Table_Macro.setShowGrid(False)
            self.Table_Macro.verticalHeader().hide()
            self.Table_Macro.setFont(self.font10)
            self.Table_Macro.setColumnCount(5)
            self.Table_Macro.setHorizontalHeaderLabels(['h (mm)', 'v (mm/s)', 'a (mm/s²)', '\u03B1 (°)', 'Atraso (s)'])
            self.Table_Macro.keyReleaseEvent = self.tableOnkeyReleaseEvent

        self.Table_Macro = QTableWidget()
        DefinirGeometria_Table_Macro()
        self.InsertDataInTable_Macro()

        #%% Gestão do layout
        if self.GravarMacro == "Gravar":
            self.Layout_Macros = QVBoxLayout()
            self.Layout_Macros.setSpacing(50)

            self.GLayout.addWidget(self.Label_Titulo,0,0,1,3)
            self.GLayout.addWidget(self.Button_Tema,0,0,1,3, Qt.AlignLeft | Qt.AlignTop)

            self.Layout_Macros.addWidget(self.ComboBox_Macros)
            self.Layout_Macros.addWidget(self.Table_Macro)

            self.Layout_Macros_Linha1 = QHBoxLayout()
            self.Layout_Macros_Linha1.addWidget(self.Button_DeletarAcao)
            self.Layout_Macros_Linha1.addWidget(self.Button_RegistrarAcao)
            self.Layout_Macros.addLayout(self.Layout_Macros_Linha1)

            self.Layout_Macros_Linha2 = QHBoxLayout()
            self.Layout_Macros_Linha2.addWidget(self.TextBox_Ciclos)
            self.Layout_Macros_Linha2.addWidget(self.Button_TestarMacro)
            self.Layout_Macros.addLayout(self.Layout_Macros_Linha2)

            self.Layout_Macros_Linha3 = QHBoxLayout()
            self.Layout_Macros_Linha3.addWidget(self.Button_RegistrarMacro)
            self.Layout_Macros_Linha3.addWidget(self.Button_CancelarMacro)
            self.Layout_Macros.addLayout(self.Layout_Macros_Linha3)

            self.Layout_Comandos.addWidget(self.Label_13)
            self.Layout_Comandos_Aceleracao_Linha0 = QHBoxLayout()
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao1)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao2)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao3)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao4)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao5)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao6)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Aceleracao_Linha0)

            self.Layout_Comandos.addWidget(self.Label_4)
            self.Layout_Comandos_Aceleracao_Linha1 = QHBoxLayout()
            self.Layout_Comandos_Aceleracao_Coluna1 = QVBoxLayout()
            self.Layout_Comandos_Aceleracao_Coluna1.addWidget(self.TextBox_Aceleracao)
            self.Layout_Comandos_Aceleracao_Coluna2 = QVBoxLayout()
            self.Layout_Comandos_Aceleracao_Coluna2.addWidget(self.Button_MaisAceleracao)
            self.Layout_Comandos_Aceleracao_Coluna2.addWidget(self.Button_MenosAceleracao)
            self.Layout_Comandos_Aceleracao_Coluna3 = QVBoxLayout()
            self.Layout_Comandos_Aceleracao_Coluna3.addWidget(self.Button_MaxAceleracao)
            self.Layout_Comandos_Aceleracao_Coluna3.addWidget(self.Button_MedAceleracao)
            self.Layout_Comandos_Aceleracao_Coluna3.addWidget(self.Button_MinAceleracao)
            self.Layout_Comandos_Aceleracao_Linha1.addLayout(self.Layout_Comandos_Aceleracao_Coluna1)
            self.Layout_Comandos_Aceleracao_Linha1.addLayout(self.Layout_Comandos_Aceleracao_Coluna2)
            self.Layout_Comandos_Aceleracao_Linha1.addLayout(self.Layout_Comandos_Aceleracao_Coluna3)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Aceleracao_Linha1)

            self.Layout_Comandos.addWidget(self.Label_5)
            self.Layout_Comandos_Velocidade_Linha1 = QHBoxLayout()
            self.Layout_Comandos_Velocidade_Coluna1 = QVBoxLayout()
            self.Layout_Comandos_Velocidade_Coluna1.addWidget(self.TextBox_Velocidade)
            self.Layout_Comandos_Velocidade_Coluna2 = QVBoxLayout()
            self.Layout_Comandos_Velocidade_Coluna2.addWidget(self.Button_MaisVelocidade)
            self.Layout_Comandos_Velocidade_Coluna2.addWidget(self.Button_MenosVelocidade)
            self.Layout_Comandos_Velocidade_Coluna3 = QVBoxLayout()
            self.Layout_Comandos_Velocidade_Coluna3.addWidget(self.Button_MaxVelocidade)
            self.Layout_Comandos_Velocidade_Coluna3.addWidget(self.Button_MedVelocidade)
            self.Layout_Comandos_Velocidade_Coluna3.addWidget(self.Button_MinVelocidade)
            self.Layout_Comandos_Velocidade_Linha1.addLayout(self.Layout_Comandos_Velocidade_Coluna1)
            self.Layout_Comandos_Velocidade_Linha1.addLayout(self.Layout_Comandos_Velocidade_Coluna2)
            self.Layout_Comandos_Velocidade_Linha1.addLayout(self.Layout_Comandos_Velocidade_Coluna3)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Velocidade_Linha1)

            self.Layout_Comandos.addWidget(self.Label_6)
            self.Layout_Comandos_Posicao_Linha1 = QHBoxLayout()
            self.Layout_Comandos_Posicao_Coluna1 = QVBoxLayout()
            self.Layout_Comandos_Posicao_Coluna1.addWidget(self.TextBox_Posicao)
            self.Layout_Comandos_Posicao_Coluna2 = QVBoxLayout()
            self.Layout_Comandos_Posicao_Coluna2.addWidget(self.Button_MaisPosicao)
            self.Layout_Comandos_Posicao_Coluna2.addWidget(self.Button_MenosPosicao)
            self.Layout_Comandos_Posicao_Coluna3 = QVBoxLayout()
            self.Layout_Comandos_Posicao_Coluna3.addWidget(self.Button_MaxPosicao)
            self.Layout_Comandos_Posicao_Coluna3.addWidget(self.Button_MedPosicao)
            self.Layout_Comandos_Posicao_Coluna3.addWidget(self.Button_MinPosicao)
            self.Layout_Comandos_Posicao_Linha1.addLayout(self.Layout_Comandos_Posicao_Coluna1)
            self.Layout_Comandos_Posicao_Linha1.addLayout(self.Layout_Comandos_Posicao_Coluna2)
            self.Layout_Comandos_Posicao_Linha1.addLayout(self.Layout_Comandos_Posicao_Coluna3)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Posicao_Linha1)

            self.Layout_Comandos.addWidget(self.Label_7)
            self.Layout_Comandos_Inclinacao_Linha1 = QHBoxLayout()
            self.Layout_Comandos_Inclinacao_Coluna1 = QVBoxLayout()
            self.Layout_Comandos_Inclinacao_Coluna1.addWidget(self.TextBox_Inclinacao)
            self.Layout_Comandos_Inclinacao_Coluna2 = QVBoxLayout()
            self.Layout_Comandos_Inclinacao_Coluna2.addWidget(self.Button_MaisInclinacao)
            self.Layout_Comandos_Inclinacao_Coluna2.addWidget(self.Button_MenosInclinacao)
            self.Layout_Comandos_Inclinacao_Coluna3 = QVBoxLayout()
            self.Layout_Comandos_Inclinacao_Coluna3.addWidget(self.Button_MaxInclinacao)
            self.Layout_Comandos_Inclinacao_Coluna3.addWidget(self.Button_MedInclinacao)
            self.Layout_Comandos_Inclinacao_Coluna3.addWidget(self.Button_MinInclinacao)
            self.Layout_Comandos_Inclinacao_Linha1.addLayout(self.Layout_Comandos_Inclinacao_Coluna1)
            self.Layout_Comandos_Inclinacao_Linha1.addLayout(self.Layout_Comandos_Inclinacao_Coluna2)
            self.Layout_Comandos_Inclinacao_Linha1.addLayout(self.Layout_Comandos_Inclinacao_Coluna3)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Inclinacao_Linha1)

            self.Layout_Comandos.addWidget(self.Label_11)
            self.Layout_Comandos.addWidget(self.Button_Executar, Qt.AlignHCenter)

            self.Layout_Status.addWidget(self.Label_8)
            self.Layout_Status.addWidget(self.Label_9)
            self.Layout_Status.addWidget(self.Label_12)
            self.Layout_Status.addWidget(self.Table_Historico)

            self.GLayout.addWidget(self.Label_1,1,0,1,1, Qt.AlignHCenter)
            self.GLayout.addLayout(self.Layout_Macros,2,0,1,1)
            self.GLayout.addWidget(self.Label_2,1,1,1,1, Qt.AlignHCenter)
            self.GLayout.addLayout(self.Layout_Comandos,2,1,1,1)
            self.GLayout.addWidget(self.Label_3,1,2,1,1, Qt.AlignHCenter)
            self.GLayout.addLayout(self.Layout_Status,2,2,1,1)
            self.GLayout.addWidget(self.Button_LimparDB,0,2, Qt.AlignTop | Qt.AlignRight)
            self.GLayout.addWidget(self.Button_VersionInfo,0,2, Qt.AlignBottom | Qt.AlignRight)
            self.GLayout.addWidget(self.Button_ArduinoConnect,0,2, Qt.AlignTop | Qt.AlignRight)

        else:
            self.Layout_Macros = QVBoxLayout()
            self.Layout_Macros.setSpacing(50)
            self.Layout_Comandos = QVBoxLayout()
            self.Layout_Status = QVBoxLayout()

            self.GLayout.addWidget(self.Label_Titulo,0,0,1,3)
            self.GLayout.addWidget(self.Button_Tema,0,0,1,3, Qt.AlignLeft | Qt.AlignTop)

            self.Layout_Macros_Linha1 = QHBoxLayout()
            self.Layout_Macros_Linha1.addWidget(self.Button_Macro1)
            self.Layout_Macros_Linha1.addWidget(self.Button_Macro2)
            self.Layout_Macros.addLayout(self.Layout_Macros_Linha1)

            self.Layout_Macros_Linha2 = QHBoxLayout()
            self.Layout_Macros_Linha2.addWidget(self.Button_Macro3)
            self.Layout_Macros_Linha2.addWidget(self.Button_Macro4)
            self.Layout_Macros.addLayout(self.Layout_Macros_Linha2)

            self.Layout_Macros_Linha3 = QHBoxLayout()
            self.Layout_Macros_Linha3.addWidget(self.Button_Macro5)
            self.Layout_Macros_Linha3.addWidget(self.Button_Macro6)
            self.Layout_Macros.addLayout(self.Layout_Macros_Linha3)

            self.Layout_Macros_Linha4 = QHBoxLayout()
            self.Layout_Macros_Linha4.addWidget(self.Button_Macro7)
            self.Layout_Macros_Linha4.addWidget(self.Button_Macro8)
            self.Layout_Macros.addLayout(self.Layout_Macros_Linha4)

            self.Layout_Macros.addWidget(self.Label_10)

            self.Layout_Macros_Linha5 = QHBoxLayout()
            self.Layout_Macros_Linha5.addWidget(self.Button_GravarMacro)
            self.Layout_Macros_Linha5.addWidget(self.Button_DeletarMacro)
            self.Layout_Macros.addLayout(self.Layout_Macros_Linha5)

            self.Layout_Comandos.addWidget(self.Label_13)
            self.Layout_Comandos_Aceleracao_Linha0 = QHBoxLayout()
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao1)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao2)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao3)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao4)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao5)
            self.Layout_Comandos_Aceleracao_Linha0.addWidget(self.Checkbox_Precisao6)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Aceleracao_Linha0)

            self.Layout_Comandos.addWidget(self.Label_4)
            self.Layout_Comandos_Aceleracao_Linha1 = QHBoxLayout()
            self.Layout_Comandos_Aceleracao_Coluna1 = QVBoxLayout()
            self.Layout_Comandos_Aceleracao_Coluna1.addWidget(self.TextBox_Aceleracao)
            self.Layout_Comandos_Aceleracao_Coluna2 = QVBoxLayout()
            self.Layout_Comandos_Aceleracao_Coluna2.addWidget(self.Button_MaisAceleracao)
            self.Layout_Comandos_Aceleracao_Coluna2.addWidget(self.Button_MenosAceleracao)
            self.Layout_Comandos_Aceleracao_Coluna3 = QVBoxLayout()
            self.Layout_Comandos_Aceleracao_Coluna3.addWidget(self.Button_MaxAceleracao)
            self.Layout_Comandos_Aceleracao_Coluna3.addWidget(self.Button_MedAceleracao)
            self.Layout_Comandos_Aceleracao_Coluna3.addWidget(self.Button_MinAceleracao)
            self.Layout_Comandos_Aceleracao_Linha1.addLayout(self.Layout_Comandos_Aceleracao_Coluna1)
            self.Layout_Comandos_Aceleracao_Linha1.addLayout(self.Layout_Comandos_Aceleracao_Coluna2)
            self.Layout_Comandos_Aceleracao_Linha1.addLayout(self.Layout_Comandos_Aceleracao_Coluna3)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Aceleracao_Linha1)

            self.Layout_Comandos.addWidget(self.Label_5)
            self.Layout_Comandos_Velocidade_Linha1 = QHBoxLayout()
            self.Layout_Comandos_Velocidade_Coluna1 = QVBoxLayout()
            self.Layout_Comandos_Velocidade_Coluna1.addWidget(self.TextBox_Velocidade)
            self.Layout_Comandos_Velocidade_Coluna2 = QVBoxLayout()
            self.Layout_Comandos_Velocidade_Coluna2.addWidget(self.Button_MaisVelocidade)
            self.Layout_Comandos_Velocidade_Coluna2.addWidget(self.Button_MenosVelocidade)
            self.Layout_Comandos_Velocidade_Coluna3 = QVBoxLayout()
            self.Layout_Comandos_Velocidade_Coluna3.addWidget(self.Button_MaxVelocidade)
            self.Layout_Comandos_Velocidade_Coluna3.addWidget(self.Button_MedVelocidade)
            self.Layout_Comandos_Velocidade_Coluna3.addWidget(self.Button_MinVelocidade)
            self.Layout_Comandos_Velocidade_Linha1.addLayout(self.Layout_Comandos_Velocidade_Coluna1)
            self.Layout_Comandos_Velocidade_Linha1.addLayout(self.Layout_Comandos_Velocidade_Coluna2)
            self.Layout_Comandos_Velocidade_Linha1.addLayout(self.Layout_Comandos_Velocidade_Coluna3)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Velocidade_Linha1)

            self.Layout_Comandos.addWidget(self.Label_6)
            self.Layout_Comandos_Posicao_Linha1 = QHBoxLayout()
            self.Layout_Comandos_Posicao_Coluna1 = QVBoxLayout()
            self.Layout_Comandos_Posicao_Coluna1.addWidget(self.TextBox_Posicao)
            self.Layout_Comandos_Posicao_Coluna2 = QVBoxLayout()
            self.Layout_Comandos_Posicao_Coluna2.addWidget(self.Button_MaisPosicao)
            self.Layout_Comandos_Posicao_Coluna2.addWidget(self.Button_MenosPosicao)
            self.Layout_Comandos_Posicao_Coluna3 = QVBoxLayout()
            self.Layout_Comandos_Posicao_Coluna3.addWidget(self.Button_MaxPosicao)
            self.Layout_Comandos_Posicao_Coluna3.addWidget(self.Button_MedPosicao)
            self.Layout_Comandos_Posicao_Coluna3.addWidget(self.Button_MinPosicao)
            self.Layout_Comandos_Posicao_Linha1.addLayout(self.Layout_Comandos_Posicao_Coluna1)
            self.Layout_Comandos_Posicao_Linha1.addLayout(self.Layout_Comandos_Posicao_Coluna2)
            self.Layout_Comandos_Posicao_Linha1.addLayout(self.Layout_Comandos_Posicao_Coluna3)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Posicao_Linha1)

            self.Layout_Comandos.addWidget(self.Label_7)
            self.Layout_Comandos_Inclinacao_Linha1 = QHBoxLayout()
            self.Layout_Comandos_Inclinacao_Coluna1 = QVBoxLayout()
            self.Layout_Comandos_Inclinacao_Coluna1.addWidget(self.TextBox_Inclinacao)
            self.Layout_Comandos_Inclinacao_Coluna2 = QVBoxLayout()
            self.Layout_Comandos_Inclinacao_Coluna2.addWidget(self.Button_MaisInclinacao)
            self.Layout_Comandos_Inclinacao_Coluna2.addWidget(self.Button_MenosInclinacao)
            self.Layout_Comandos_Inclinacao_Coluna3 = QVBoxLayout()
            self.Layout_Comandos_Inclinacao_Coluna3.addWidget(self.Button_MaxInclinacao)
            self.Layout_Comandos_Inclinacao_Coluna3.addWidget(self.Button_MedInclinacao)
            self.Layout_Comandos_Inclinacao_Coluna3.addWidget(self.Button_MinInclinacao)
            self.Layout_Comandos_Inclinacao_Linha1.addLayout(self.Layout_Comandos_Inclinacao_Coluna1)
            self.Layout_Comandos_Inclinacao_Linha1.addLayout(self.Layout_Comandos_Inclinacao_Coluna2)
            self.Layout_Comandos_Inclinacao_Linha1.addLayout(self.Layout_Comandos_Inclinacao_Coluna3)
            self.Layout_Comandos.addLayout(self.Layout_Comandos_Inclinacao_Linha1)

            self.Layout_Comandos.addWidget(self.Label_11)
            self.Layout_Comandos.addWidget(self.Button_Executar, Qt.AlignHCenter)

            self.Layout_Status.addWidget(self.Label_8)
            self.Layout_Status.addWidget(self.Label_9)
            self.Layout_Status.addWidget(self.Label_12)
            self.Layout_Status.addWidget(self.Table_Historico)

            self.GLayout.addWidget(self.Label_1,1,0,1,1, Qt.AlignHCenter)
            self.GLayout.addLayout(self.Layout_Macros,2,0,1,1)
            self.GLayout.addWidget(self.Label_2,1,1,1,1, Qt.AlignHCenter)
            self.GLayout.addLayout(self.Layout_Comandos,2,1,1,1)
            self.GLayout.addWidget(self.Label_3,1,2,1,1, Qt.AlignHCenter)
            self.GLayout.addLayout(self.Layout_Status,2,2,1,1)
            self.GLayout.addWidget(self.Button_LimparDB,0,2, Qt.AlignTop | Qt.AlignRight)
            self.GLayout.addWidget(self.Button_VersionInfo,0,2, Qt.AlignBottom | Qt.AlignRight)
            self.GLayout.addWidget(self.Button_ArduinoConnect,0,2, Qt.AlignTop | Qt.AlignRight)

#%% Outros
    def InsertDataInTable_Historio(self):
        self.data = self.DBManager.GetAllMoves()
        self.data = self.data[::-1]
        self.Table_Historico.setRowCount(len(self.data))

        for i, item in enumerate(self.data):
            it = self.Table_Historico.item(i, 0)
            text = str("h="+str(item[0])+"mm | "+
                        "v="+str(item[1])+"mm/s | "+
                        "a="+str(item[2])+"mm/s² | "+
                        "\u03B1="+str(item[3])+"°")
            it = QTableWidgetItem(text)
            it.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable)) # Desabilita selecionar o item
            it.setFlags(it.flags() & ~Qt.ItemIsEditable) # Desabilita a edição do item
            it.setTextAlignment(Qt.AlignCenter)
            it.setForeground(QBrush(QColor('black')))
            self.Table_Historico.setItem(i, 0, it)
        self.Table_Historico.adjustSize()
        self.Table_Historico.setColumnWidth(0, 260)

    def InsertDataInTable_Macro(self):
        self.dataMacro = self.DBManager.GetMacroMoves(self.ComboBox_Macros.currentIndex())
        if len(self.dataMacro)>0: self.TextBox_Ciclos.setText(str(self.dataMacro[0][5]))
        self.Table_Macro.setRowCount(len(self.dataMacro))

        for i, item in enumerate(self.dataMacro):
            for j in range(len(item)):
                if not j == 6:
                    it = self.Table_Macro.item(i, j)
                    text = str(item[j])
                    it = QTableWidgetItem(text)
                    if not j == 4:
                        it.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable)) # Desabilita selecionar o item
                        it.setFlags(it.flags() & ~Qt.ItemIsEditable) # Desabilita a edição do item
                    it.setTextAlignment(Qt.AlignCenter)
                    it.setForeground(QBrush(QColor('black')))
                    self.Table_Macro.setItem(i, j, it)
        self.Table_Macro.adjustSize()
        for i in range(5):
            self.Table_Macro.setColumnWidth(i, int(self.frameGeometry().width()*2/7/5))

    def ClearPage(self):
        self.Label_Titulo.deleteLater()
        self.Label_1.deleteLater()
        self.Label_2.deleteLater()
        self.Label_3.deleteLater()
        self.Label_4.deleteLater()
        self.Label_5.deleteLater()
        self.Label_6.deleteLater()
        self.Label_7.deleteLater()
        self.Label_8.deleteLater()
        self.Label_9.deleteLater()
        self.Label_10.deleteLater()
        self.Label_11.deleteLater()
        self.Label_12.deleteLater()
        self.Label_13.deleteLater()
        self.Button_Tema.deleteLater()
        self.Button_Macro1.deleteLater()
        self.Button_Macro2.deleteLater()
        self.Button_Macro3.deleteLater()
        self.Button_Macro4.deleteLater()
        self.Button_Macro5.deleteLater()
        self.Button_Macro6.deleteLater()
        self.Button_Macro7.deleteLater()
        self.Button_Macro8.deleteLater()
        self.Button_GravarMacro.deleteLater()
        self.Button_DeletarMacro.deleteLater()
        self.Button_MaisAceleracao.deleteLater()
        self.Button_MenosAceleracao.deleteLater()
        self.Button_MaisVelocidade.deleteLater()
        self.Button_MenosVelocidade.deleteLater()
        self.Button_MaisPosicao.deleteLater()
        self.Button_MenosPosicao.deleteLater()
        self.Button_MaisInclinacao.deleteLater()
        self.Button_MenosInclinacao.deleteLater()
        self.Button_MaxAceleracao.deleteLater()
        self.Button_MedAceleracao.deleteLater()
        self.Button_MinAceleracao.deleteLater()
        self.Button_MaxVelocidade.deleteLater()
        self.Button_MedVelocidade.deleteLater()
        self.Button_MinVelocidade.deleteLater()
        self.Button_MaxPosicao.deleteLater()
        self.Button_MedPosicao.deleteLater()
        self.Button_MinPosicao.deleteLater()
        self.Button_MaxInclinacao.deleteLater()
        self.Button_MedInclinacao.deleteLater()
        self.Button_MinInclinacao.deleteLater()
        self.Button_LimparDB.deleteLater()
        self.Button_Executar.deleteLater()
        self.Button_LimparDB.deleteLater()
        self.Button_DeletarAcao.deleteLater()
        self.Button_RegistrarAcao.deleteLater()
        self.Button_TestarMacro.deleteLater()
        self.Button_RegistrarMacro.deleteLater()
        self.Button_CancelarMacro.deleteLater()
        self.TextBox_Aceleracao.deleteLater()
        self.TextBox_Velocidade.deleteLater()
        self.TextBox_Posicao.deleteLater()
        self.TextBox_Inclinacao.deleteLater()
        self.TextBox_Ciclos.deleteLater()
        self.Table_Historico.deleteLater()
        self.Table_Macro.deleteLater()
        self.ComboBox_Macros.deleteLater()
        self.Checkbox_Precisao1.deleteLater()
        self.Checkbox_Precisao2.deleteLater()
        self.Checkbox_Precisao3.deleteLater()
        self.Checkbox_Precisao4.deleteLater()
        self.Checkbox_Precisao5.deleteLater()
        self.Checkbox_Precisao6.deleteLater()
        self.GroupCheckbox_Precisao.deleteLater()

        if self.GravarMacro == "Gravar":
            self.Layout_Macros.removeItem(self.Layout_Macros_Linha1)
            self.Layout_Macros.removeItem(self.Layout_Macros_Linha2)
            self.Layout_Macros.removeItem(self.Layout_Macros_Linha3)

            self.Layout_Comandos_Aceleracao_Linha1.removeItem(self.Layout_Comandos_Aceleracao_Coluna1)
            self.Layout_Comandos_Aceleracao_Linha1.removeItem(self.Layout_Comandos_Aceleracao_Coluna2)
            self.Layout_Comandos_Aceleracao_Linha1.removeItem(self.Layout_Comandos_Aceleracao_Coluna3)
            self.Layout_Comandos.removeItem(self.Layout_Comandos_Aceleracao_Linha1)

            self.Layout_Comandos_Velocidade_Linha1.removeItem(self.Layout_Comandos_Velocidade_Coluna1)
            self.Layout_Comandos_Velocidade_Linha1.removeItem(self.Layout_Comandos_Velocidade_Coluna2)
            self.Layout_Comandos_Velocidade_Linha1.removeItem(self.Layout_Comandos_Velocidade_Coluna3)
            self.Layout_Comandos.removeItem(self.Layout_Comandos_Velocidade_Linha1)

            self.Layout_Comandos_Posicao_Linha1.removeItem(self.Layout_Comandos_Posicao_Coluna1)
            self.Layout_Comandos_Posicao_Linha1.removeItem(self.Layout_Comandos_Posicao_Coluna2)
            self.Layout_Comandos_Posicao_Linha1.removeItem(self.Layout_Comandos_Posicao_Coluna3)
            self.Layout_Comandos.removeItem(self.Layout_Comandos_Posicao_Linha1)

            self.Layout_Comandos_Inclinacao_Linha1.removeItem(self.Layout_Comandos_Inclinacao_Coluna1)
            self.Layout_Comandos_Inclinacao_Linha1.removeItem(self.Layout_Comandos_Inclinacao_Coluna2)
            self.Layout_Comandos_Inclinacao_Linha1.removeItem(self.Layout_Comandos_Inclinacao_Coluna3)
            self.Layout_Comandos.removeItem(self.Layout_Comandos_Inclinacao_Linha1)

            self.GLayout.removeItem(self.Layout_Macros)
            self.GLayout.removeItem(self.Layout_Comandos)
            self.GLayout.removeItem(self.Layout_Status)
        else:
            self.Layout_Macros.removeItem(self.Layout_Macros_Linha1)
            self.Layout_Macros.removeItem(self.Layout_Macros_Linha2)
            self.Layout_Macros.removeItem(self.Layout_Macros_Linha3)
            self.Layout_Macros.removeItem(self.Layout_Macros_Linha4)
            self.Layout_Macros.removeItem(self.Layout_Macros_Linha5)

            self.Layout_Comandos_Aceleracao_Linha1.removeItem(self.Layout_Comandos_Aceleracao_Coluna1)
            self.Layout_Comandos_Aceleracao_Linha1.removeItem(self.Layout_Comandos_Aceleracao_Coluna2)
            self.Layout_Comandos_Aceleracao_Linha1.removeItem(self.Layout_Comandos_Aceleracao_Coluna3)
            self.Layout_Comandos.removeItem(self.Layout_Comandos_Aceleracao_Linha1)

            self.Layout_Comandos_Velocidade_Linha1.removeItem(self.Layout_Comandos_Velocidade_Coluna1)
            self.Layout_Comandos_Velocidade_Linha1.removeItem(self.Layout_Comandos_Velocidade_Coluna2)
            self.Layout_Comandos_Velocidade_Linha1.removeItem(self.Layout_Comandos_Velocidade_Coluna3)
            self.Layout_Comandos.removeItem(self.Layout_Comandos_Velocidade_Linha1)

            self.Layout_Comandos_Posicao_Linha1.removeItem(self.Layout_Comandos_Posicao_Coluna1)
            self.Layout_Comandos_Posicao_Linha1.removeItem(self.Layout_Comandos_Posicao_Coluna2)
            self.Layout_Comandos_Posicao_Linha1.removeItem(self.Layout_Comandos_Posicao_Coluna3)
            self.Layout_Comandos.removeItem(self.Layout_Comandos_Posicao_Linha1)

            self.Layout_Comandos_Inclinacao_Linha1.removeItem(self.Layout_Comandos_Inclinacao_Coluna1)
            self.Layout_Comandos_Inclinacao_Linha1.removeItem(self.Layout_Comandos_Inclinacao_Coluna2)
            self.Layout_Comandos_Inclinacao_Linha1.removeItem(self.Layout_Comandos_Inclinacao_Coluna3)
            self.Layout_Comandos.removeItem(self.Layout_Comandos_Inclinacao_Linha1)

            self.GLayout.removeItem(self.Layout_Macros)
            self.GLayout.removeItem(self.Layout_Comandos)
            self.GLayout.removeItem(self.Layout_Status)

    def OnButtonPressed(self, ButtonPressed):
        if ButtonPressed == 'Mudar tema':
            # Troca tema e aplica
            if self.backgroundStyle == 'Dark': self.backgroundStyle = 'Bright'
            else: self.backgroundStyle = 'Dark'

            if self.backgroundStyle == 'Dark':
                BackgroundColor = 'black'
                BackgroundColor2 = 'gray'
                FontColor = 'white'
            else:
                BackgroundColor = 'gray'
                BackgroundColor2 = 'white'
                FontColor = 'black'
            background = self.palette()
            background.setColor(self.backgroundRole(), QColor(BackgroundColor))
            self.setPalette(background)
            self.Background_1.setStyleSheet("background-color: "+BackgroundColor)

            self.Label_Titulo.setStyleSheet('color: '+FontColor)
            self.Label_1.setStyleSheet('color: '+FontColor)
            self.Label_2.setStyleSheet('color: '+FontColor)
            self.Label_3.setStyleSheet('color: '+FontColor)
            self.Label_4.setStyleSheet('color: '+FontColor)
            self.Label_5.setStyleSheet('color: '+FontColor)
            self.Label_6.setStyleSheet('color: '+FontColor)
            self.Label_7.setStyleSheet('color: '+FontColor)
            self.Label_8.setStyleSheet('color: '+FontColor)
            self.Label_9.setStyleSheet('color: '+FontColor)

            self.Button_Tema.setStyleSheet("background-color: "+BackgroundColor+"; border: none; outline: none;")
            self.Button_Macro1.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_Macro2.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_Macro3.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_Macro4.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_Macro5.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_Macro6.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_Macro7.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_Macro8.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_GravarMacro.setStyleSheet("background-color: "+BackgroundColor2+"; color: border: none; outline: none;")
            self.Button_DeletarMacro.setStyleSheet("background-color: "+BackgroundColor2+"; color: border: none; outline: none;")
            self.Button_MaisAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MenosAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MaisVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MenosVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MaisPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MenosPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MaisInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MenosInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MaxAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MedAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MinAceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MaxVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MedVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MinVelocidade.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MaxPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MedPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MinPosicao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MaxInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MedInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_MinInclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            # self.Button_Executar.setStyleSheet("background-color: "+BackgroundColor2+"; color: border: none; outline: none;")
            self.Button_LimparDB.setStyleSheet("background-color: "+BackgroundColor+"; border: none; outline: none;")
            # self.Button_DeletarAcao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            # self.Button_RegistrarAcao.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.Button_TestarMacro.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.TextBox_Aceleracao.setStyleSheet("background-color: "+BackgroundColor2+"; color: black;  border: none; outline: none;")
            self.TextBox_Velocidade.setStyleSheet("background-color: "+BackgroundColor2+"; color: black;  border: none; outline: none;")
            self.TextBox_Posicao.setStyleSheet("background-color: "+BackgroundColor2+"; color: black;  border: none; outline: none;")
            self.TextBox_Inclinacao.setStyleSheet("background-color: "+BackgroundColor2+"; color: black;  border: none; outline: none;")
            self.TextBox_Ciclos.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.ComboBox_Macros.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            self.edit.setStyleSheet("background-color: "+BackgroundColor2+"; border: none; outline: none;")
            if self.backgroundStyle == 'Dark': self.Button_LimparDB.setIcon(QIcon("./images/Limpar DB - Tema escuro.png"))
            else: self.Button_LimparDB.setIcon(QIcon("./images/Limpar DB.png"))

        elif ButtonPressed == 'Macro1':
            if self.ArduinoComm.Connected:
                if not self.MacroRunning:
                    self.MacroRunning = True
                    ToSave = False
                    comandos = self.DBManager.GetMacroMoves(0)
                    comandos = comandos[::-1]
                    if len(comandos)>0:
                        MessageBox_Msg1 = QMessageBox()
                        MessageBox_Msg1.setWindowTitle("Salvar em CSV")
                        MessageBox_Msg1.setText("Deseja salvar os comandos em um arquivo CSV?")
                        MessageBox_Msg1.setIcon(QMessageBox.Question)
                        MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                        MessageBox_Msg1.setDefaultButton(QMessageBox.No)
                        MessageBox_Msg1.setWindowIcon(QIcon(".\images\save.png"))
                        returnValue = MessageBox_Msg1.exec()
                        if returnValue == QMessageBox.Yes:
                            root = tkinter.Tk()
                            root.withdraw() # use to hide tkinter window
                            if not self.filedialogIsOpen:
                                self.filedialogIsOpen = True
                                FilePath_SaveAs = filedialog.asksaveasfilename(title='Selecione a pasta para salvar seu resultado CSV', filetypes=[("CSV files", "*.csv")])
                                self.filedialogIsOpen = False
                                if not len(FilePath_SaveAs)>0:
                                    self.MacroRunning = False # Cancela a execução da macro
                                    QMessageBox.warning(self, 'Aviso', 'Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado.')
                                else: ToSave = True
                        if self.MacroRunning:
                            if ToSave:
                                f = open(FilePath_SaveAs.replace(".csv","")+".csv", 'w', newline='', encoding='utf-8')
                                w = csv.writer(f)
                                w.writerow(["Execucao da macro "+self.Button_Macro1.text()])
                            for ciclo in range(comandos[0][5]):
                                print("Ciclo",ciclo+1)
                                if ToSave:
                                    w.writerow(["Ciclo "+str(ciclo+1)])
                                    w.writerow(["h (mm)", "v (mm/s)", "a (mm/s2)", "\alpha (graus)","Atraso (s)"])
                                for comando in comandos:
                                    self.DBManager.WriteOnDB([comando[0],comando[1],comando[2],comando[3]])
                                    self.Table_Historico.clear()
                                    self.InsertDataInTable_Historio()
                                    self.Label_8.setText("Posição atual\n"+str(comando[0])+"mm")
                                    self.Label_9.setText("Inclinação atual\n"+str(comando[1])+"°")
                                    self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                    if ToSave: w.writerow([comando[0],comando[1],comando[2],comando[3],comando[4]])
                            if ToSave:
                                # Pedir Observação
                                observacao, done = QInputDialog.getText(self, 'Obs', 'Insira uma observação (opcional):')
                                # Salvar comandos e observação em CSV
                                w.writerow(["Observacao",observacao])
                                f.close()
                    else:
                        QMessageBox.warning(self, 'Aviso', 'Não há nada registrado nessa macro.')
                    self.MacroRunning = False
                else:
                    QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'Macro2':
            if self.ArduinoComm.Connected:
                if not self.MacroRunning:
                    self.MacroRunning = True
                    ToSave = False
                    comandos = self.DBManager.GetMacroMoves(1)
                    comandos = comandos[::-1]
                    if len(comandos)>0:
                        MessageBox_Msg1 = QMessageBox()
                        MessageBox_Msg1.setWindowTitle("Salvar em CSV")
                        MessageBox_Msg1.setText("Deseja salvar os comandos em um arquivo CSV?")
                        MessageBox_Msg1.setIcon(QMessageBox.Question)
                        MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                        MessageBox_Msg1.setDefaultButton(QMessageBox.No)
                        MessageBox_Msg1.setWindowIcon(QIcon(".\images\save.png"))
                        returnValue = MessageBox_Msg1.exec()
                        if returnValue == QMessageBox.Yes:
                            root = tkinter.Tk()
                            root.withdraw() # use to hide tkinter window
                            if not self.filedialogIsOpen:
                                self.filedialogIsOpen = True
                                FilePath_SaveAs = filedialog.asksaveasfilename(title='Selecione a pasta para salvar seu resultado CSV', filetypes=[("CSV files", "*.csv")])
                                self.filedialogIsOpen = False
                                if not len(FilePath_SaveAs)>0:
                                    self.MacroRunning = False # Cancela a execução da macro
                                    QMessageBox.warning(self, 'Aviso', 'Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado.')
                                else: ToSave = True
                            if self.MacroRunning:
                                if ToSave:
                                    f = open(FilePath_SaveAs.replace(".csv","")+".csv", 'w', newline='', encoding='utf-8')
                                    w = csv.writer(f)
                                    w.writerow(["Execucao da macro "+self.Button_Macro2.text()])
                                for ciclo in range(comandos[0][5]):
                                    print("Ciclo",ciclo+1)
                                    if ToSave:
                                        w.writerow(["Ciclo "+str(ciclo+1)])
                                        w.writerow(["h (mm)", "v (mm/s)", "a (mm/s2)", "\alpha (graus)","Atraso (s)"])
                                    for comando in comandos:
                                        self.DBManager.WriteOnDB([comando[0],comando[1],comando[2],comando[3]])
                                        self.Table_Historico.clear()
                                        self.InsertDataInTable_Historio()
                                        self.Label_8.setText("Posição atual\n"+str(comando[0])+"mm")
                                        self.Label_9.setText("Inclinação atual\n"+str(comando[1])+"°")
                                        self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                        if ToSave: w.writerow([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                if ToSave:
                                    # Pedir Observação
                                    observacao, done = QInputDialog.getText(self, 'Obs', 'Insira uma observação (opcional):')
                                    # Salvar comandos e observação em CSV
                                    w.writerow(["Observacao",observacao])
                                    f.close()
                            else:
                                QMessageBox.warning(self, 'Aviso', 'Não há nada registrado nessa macro.')
                    self.MacroRunning = False
                else:
                    QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'Macro3':
            if self.ArduinoComm.Connected:
                if not self.MacroRunning:
                    self.MacroRunning = True
                    ToSave = False
                    comandos = self.DBManager.GetMacroMoves(2)
                    comandos = comandos[::-1]
                    if len(comandos)>0:
                        MessageBox_Msg1 = QMessageBox()
                        MessageBox_Msg1.setWindowTitle("Salvar em CSV")
                        MessageBox_Msg1.setText("Deseja salvar os comandos em um arquivo CSV?")
                        MessageBox_Msg1.setIcon(QMessageBox.Question)
                        MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                        MessageBox_Msg1.setDefaultButton(QMessageBox.No)
                        MessageBox_Msg1.setWindowIcon(QIcon(".\images\save.png"))
                        returnValue = MessageBox_Msg1.exec()
                        if returnValue == QMessageBox.Yes:
                            root = tkinter.Tk()
                            root.withdraw() # use to hide tkinter window
                            if not self.filedialogIsOpen:
                                self.filedialogIsOpen = True
                                FilePath_SaveAs = filedialog.asksaveasfilename(title='Selecione a pasta para salvar seu resultado CSV', filetypes=[("CSV files", "*.csv")])
                                self.filedialogIsOpen = False
                                if not len(FilePath_SaveAs)>0:
                                    self.MacroRunning = False # Cancela a execução da macro
                                    QMessageBox.warning(self, 'Aviso', 'Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado.')
                                else: ToSave = True
                            if self.MacroRunning:
                                if ToSave:
                                    f = open(FilePath_SaveAs.replace(".csv","")+".csv", 'w', newline='', encoding='utf-8')
                                    w = csv.writer(f)
                                    w.writerow(["Execucao da macro "+self.Button_Macro3.text()])
                                for ciclo in range(comandos[0][5]):
                                    print("Ciclo",ciclo+1)
                                    if ToSave:
                                        w.writerow(["Ciclo "+str(ciclo+1)])
                                        w.writerow(["h (mm)", "v (mm/s)", "a (mm/s2)", "\alpha (graus)","Atraso (s)"])
                                    for comando in comandos:
                                        self.DBManager.WriteOnDB([comando[0],comando[1],comando[2],comando[3]])
                                        self.Table_Historico.clear()
                                        self.InsertDataInTable_Historio()
                                        self.Label_8.setText("Posição atual\n"+str(comando[0])+"mm")
                                        self.Label_9.setText("Inclinação atual\n"+str(comando[1])+"°")
                                        self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                        if ToSave: w.writerow([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                if ToSave:
                                    # Pedir Observação
                                    observacao, done = QInputDialog.getText(self, 'Obs', 'Insira uma observação (opcional):')
                                    # Salvar comandos e observação em CSV
                                    w.writerow(["Observacao",observacao])
                                    f.close()
                            else:
                                QMessageBox.warning(self, 'Aviso', 'Não há nada registrado nessa macro.')
                    self.MacroRunning = False
                else:
                    QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'Macro4':
            if self.ArduinoComm.Connected:
                if not self.MacroRunning:
                    self.MacroRunning = True
                    ToSave = False
                    comandos = self.DBManager.GetMacroMoves(3)
                    comandos = comandos[::-1]
                    if len(comandos)>0:
                        MessageBox_Msg1 = QMessageBox()
                        MessageBox_Msg1.setWindowTitle("Salvar em CSV")
                        MessageBox_Msg1.setText("Deseja salvar os comandos em um arquivo CSV?")
                        MessageBox_Msg1.setIcon(QMessageBox.Question)
                        MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                        MessageBox_Msg1.setDefaultButton(QMessageBox.No)
                        MessageBox_Msg1.setWindowIcon(QIcon(".\images\save.png"))
                        returnValue = MessageBox_Msg1.exec()
                        if returnValue == QMessageBox.Yes:
                            root = tkinter.Tk()
                            root.withdraw() # use to hide tkinter window
                            if not self.filedialogIsOpen:
                                self.filedialogIsOpen = True
                                FilePath_SaveAs = filedialog.asksaveasfilename(title='Selecione a pasta para salvar seu resultado CSV', filetypes=[("CSV files", "*.csv")])
                                self.filedialogIsOpen = False
                                if not len(FilePath_SaveAs)>0:
                                    self.MacroRunning = False # Cancela a execução da macro
                                    QMessageBox.warning(self, 'Aviso', 'Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado.')
                                else: ToSave = True
                            if self.MacroRunning:
                                if ToSave:
                                    f = open(FilePath_SaveAs.replace(".csv","")+".csv", 'w', newline='', encoding='utf-8')
                                    w = csv.writer(f)
                                    w.writerow(["Execucao da macro "+self.Button_Macro4.text()])
                                for ciclo in range(comandos[0][5]):
                                    print("Ciclo",ciclo+1)
                                    if ToSave:
                                        w.writerow(["Ciclo "+str(ciclo+1)])
                                        w.writerow(["h (mm)", "v (mm/s)", "a (mm/s2)", "\alpha (graus)","Atraso (s)"])
                                    for comando in comandos:
                                        self.DBManager.WriteOnDB([comando[0],comando[1],comando[2],comando[3]])
                                        self.Table_Historico.clear()
                                        self.InsertDataInTable_Historio()
                                        self.Label_8.setText("Posição atual\n"+str(comando[0])+"mm")
                                        self.Label_9.setText("Inclinação atual\n"+str(comando[1])+"°")
                                        self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                        if ToSave: w.writerow([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                if ToSave:
                                    # Pedir Observação
                                    observacao, done = QInputDialog.getText(self, 'Obs', 'Insira uma observação (opcional):')
                                    # Salvar comandos e observação em CSV
                                    w.writerow(["Observacao",observacao])
                                    f.close()
                    else:
                        QMessageBox.warning(self, 'Aviso', 'Não há nada registrado nessa macro.')
                    self.MacroRunning = False
                else:
                    QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'Macro5':
            if self.ArduinoComm.Connected:
                if not self.MacroRunning:
                    self.MacroRunning = True
                    ToSave = False
                    comandos = self.DBManager.GetMacroMoves(4)
                    comandos = comandos[::-1]
                    if len(comandos)>0:
                        MessageBox_Msg1 = QMessageBox()
                        MessageBox_Msg1.setWindowTitle("Salvar em CSV")
                        MessageBox_Msg1.setText("Deseja salvar os comandos em um arquivo CSV?")
                        MessageBox_Msg1.setIcon(QMessageBox.Question)
                        MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                        MessageBox_Msg1.setDefaultButton(QMessageBox.No)
                        MessageBox_Msg1.setWindowIcon(QIcon(".\images\save.png"))
                        returnValue = MessageBox_Msg1.exec()
                        if returnValue == QMessageBox.Yes:
                            root = tkinter.Tk()
                            root.withdraw() # use to hide tkinter window
                            if not self.filedialogIsOpen:
                                self.filedialogIsOpen = True
                                FilePath_SaveAs = filedialog.asksaveasfilename(title='Selecione a pasta para salvar seu resultado CSV', filetypes=[("CSV files", "*.csv")])
                                self.filedialogIsOpen = False
                                if not len(FilePath_SaveAs)>0:
                                    self.MacroRunning = False # Cancela a execução da macro
                                    QMessageBox.warning(self, 'Aviso', 'Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado.')
                                else: ToSave = True
                            if self.MacroRunning:
                                if ToSave:
                                    f = open(FilePath_SaveAs.replace(".csv","")+".csv", 'w', newline='', encoding='utf-8')
                                    w = csv.writer(f)
                                    w.writerow(["Execucao da macro "+self.Button_Macro5.text()])
                                for ciclo in range(comandos[0][5]):
                                    print("Ciclo",ciclo+1)
                                    if ToSave:
                                        w.writerow(["Ciclo "+str(ciclo+1)])
                                        w.writerow(["h (mm)", "v (mm/s)", "a (mm/s2)", "\alpha (graus)","Atraso (s)"])
                                    for comando in comandos:
                                        self.DBManager.WriteOnDB([comando[0],comando[1],comando[2],comando[3]])
                                        self.Table_Historico.clear()
                                        self.InsertDataInTable_Historio()
                                        self.Label_8.setText("Posição atual\n"+str(comando[0])+"mm")
                                        self.Label_9.setText("Inclinação atual\n"+str(comando[1])+"°")
                                        self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                        if ToSave: w.writerow([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                if ToSave:
                                    # Pedir Observação
                                    observacao, done = QInputDialog.getText(self, 'Obs', 'Insira uma observação (opcional):')
                                    # Salvar comandos e observação em CSV
                                    w.writerow(["Observacao",observacao])
                                    f.close()
                            else:
                                QMessageBox.warning(self, 'Aviso', 'Não há nada registrado nessa macro.')
                    self.MacroRunning = False
                else:
                    QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'Macro6':
            if self.ArduinoComm.Connected:
                if not self.MacroRunning:
                    self.MacroRunning = True
                    ToSave = False
                    comandos = self.DBManager.GetMacroMoves(5)
                    comandos = comandos[::-1]
                    if len(comandos)>0:
                        MessageBox_Msg1 = QMessageBox()
                        MessageBox_Msg1.setWindowTitle("Salvar em CSV")
                        MessageBox_Msg1.setText("Deseja salvar os comandos em um arquivo CSV?")
                        MessageBox_Msg1.setIcon(QMessageBox.Question)
                        MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                        MessageBox_Msg1.setDefaultButton(QMessageBox.No)
                        MessageBox_Msg1.setWindowIcon(QIcon(".\images\save.png"))
                        returnValue = MessageBox_Msg1.exec()
                        if returnValue == QMessageBox.Yes:
                            root = tkinter.Tk()
                            root.withdraw() # use to hide tkinter window
                            if not self.filedialogIsOpen:
                                self.filedialogIsOpen = True
                                FilePath_SaveAs = filedialog.asksaveasfilename(title='Selecione a pasta para salvar seu resultado CSV', filetypes=[("CSV files", "*.csv")])
                                self.filedialogIsOpen = False
                                if not len(FilePath_SaveAs)>0:
                                    self.MacroRunning = False # Cancela a execução da macro
                                    QMessageBox.warning(self, 'Aviso', 'Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado.')
                                else: ToSave = True
                            if self.MacroRunning:
                                if ToSave:
                                    f = open(FilePath_SaveAs.replace(".csv","")+".csv", 'w', newline='', encoding='utf-8')
                                    w = csv.writer(f)
                                    w.writerow(["Execucao da macro "+self.Button_Macro6.text()])
                                for ciclo in range(comandos[0][5]):
                                    print("Ciclo",ciclo+1)
                                    if ToSave:
                                        w.writerow(["Ciclo "+str(ciclo+1)])
                                        w.writerow(["h (mm)", "v (mm/s)", "a (mm/s2)", "\alpha (graus)","Atraso (s)"])
                                    for comando in comandos:
                                        self.DBManager.WriteOnDB([comando[0],comando[1],comando[2],comando[3]])
                                        self.Table_Historico.clear()
                                        self.InsertDataInTable_Historio()
                                        self.Label_8.setText("Posição atual\n"+str(comando[0])+"mm")
                                        self.Label_9.setText("Inclinação atual\n"+str(comando[1])+"°")
                                        self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                        if ToSave: w.writerow([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                if ToSave:
                                    # Pedir Observação
                                    observacao, done = QInputDialog.getText(self, 'Obs', 'Insira uma observação (opcional):')
                                    # Salvar comandos e observação em CSV
                                    w.writerow(["Observacao",observacao])
                                    f.close()
                            else:
                                QMessageBox.warning(self, 'Aviso', 'Não há nada registrado nessa macro.')
                    self.MacroRunning = False
                else:
                    QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'Macro7':
            if self.ArduinoComm.Connected:
                if not self.MacroRunning:
                    self.MacroRunning = True
                    ToSave = False
                    comandos = self.DBManager.GetMacroMoves(6)
                    comandos = comandos[::-1]
                    if len(comandos)>0:
                        MessageBox_Msg1 = QMessageBox()
                        MessageBox_Msg1.setWindowTitle("Salvar em CSV")
                        MessageBox_Msg1.setText("Deseja salvar os comandos em um arquivo CSV?")
                        MessageBox_Msg1.setIcon(QMessageBox.Question)
                        MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                        MessageBox_Msg1.setDefaultButton(QMessageBox.No)
                        MessageBox_Msg1.setWindowIcon(QIcon(".\images\save.png"))
                        returnValue = MessageBox_Msg1.exec()
                        if returnValue == QMessageBox.Yes:
                            root = tkinter.Tk()
                            root.withdraw() # use to hide tkinter window
                            if not self.filedialogIsOpen:
                                self.filedialogIsOpen = True
                                FilePath_SaveAs = filedialog.asksaveasfilename(title='Selecione a pasta para salvar seu resultado CSV', filetypes=[("CSV files", "*.csv")])
                                self.filedialogIsOpen = False
                                if not len(FilePath_SaveAs)>0:
                                    self.MacroRunning = False # Cancela a execução da macro
                                    QMessageBox.warning(self, 'Aviso', 'Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado.')
                                else: ToSave = True
                            if self.MacroRunning:
                                if ToSave:
                                    f = open(FilePath_SaveAs.replace(".csv","")+".csv", 'w', newline='', encoding='utf-8')
                                    w = csv.writer(f)
                                    w.writerow(["Execucao da macro "+self.Button_Macro7.text()])
                                for ciclo in range(comandos[0][5]):
                                    print("Ciclo",ciclo+1)
                                    if ToSave:
                                        w.writerow(["Ciclo "+str(ciclo+1)])
                                        w.writerow(["h (mm)", "v (mm/s)", "a (mm/s2)", "\alpha (graus)","Atraso (s)"])
                                    for comando in comandos:
                                        self.DBManager.WriteOnDB([comando[0],comando[1],comando[2],comando[3]])
                                        self.Table_Historico.clear()
                                        self.InsertDataInTable_Historio()
                                        self.Label_8.setText("Posição atual\n"+str(comando[0])+"mm")
                                        self.Label_9.setText("Inclinação atual\n"+str(comando[1])+"°")
                                        self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                        if ToSave: w.writerow([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                if ToSave:
                                    # Pedir Observação
                                    observacao, done = QInputDialog.getText(self, 'Obs', 'Insira uma observação (opcional):')
                                    # Salvar comandos e observação em CSV
                                    w.writerow(["Observacao",observacao])
                                    f.close()
                            else:
                                QMessageBox.warning(self, 'Aviso', 'Não há nada registrado nessa macro.')
                    self.MacroRunning = False
                else:
                    QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'Macro8':
            if self.ArduinoComm.Connected:
                if not self.MacroRunning:
                    self.MacroRunning = True
                    ToSave = False
                    comandos = self.DBManager.GetMacroMoves(7)
                    comandos = comandos[::-1]
                    if len(comandos)>0:
                        MessageBox_Msg1 = QMessageBox()
                        MessageBox_Msg1.setWindowTitle("Salvar em CSV")
                        MessageBox_Msg1.setText("Deseja salvar os comandos em um arquivo CSV?")
                        MessageBox_Msg1.setIcon(QMessageBox.Question)
                        MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
                        MessageBox_Msg1.setDefaultButton(QMessageBox.No)
                        MessageBox_Msg1.setWindowIcon(QIcon(".\images\save.png"))
                        returnValue = MessageBox_Msg1.exec()
                        if returnValue == QMessageBox.Yes:
                            root = tkinter.Tk()
                            root.withdraw() # use to hide tkinter window
                            if not self.filedialogIsOpen:
                                self.filedialogIsOpen = True
                                FilePath_SaveAs = filedialog.asksaveasfilename(title='Selecione a pasta para salvar seu resultado CSV', filetypes=[("CSV files", "*.csv")])
                                self.filedialogIsOpen = False
                                if not len(FilePath_SaveAs)>0:
                                    self.MacroRunning = False # Cancela a execução da macro
                                    QMessageBox.warning(self, 'Aviso', 'Execução cancelada.\nMotivo:\nO caminho do CSV não foi especificado.')
                                else: ToSave = True
                            if self.MacroRunning:
                                if ToSave:
                                    f = open(FilePath_SaveAs.replace(".csv","")+".csv", 'w', newline='', encoding='utf-8')
                                    w = csv.writer(f)
                                    w.writerow(["Execucao da macro "+self.Button_Macro8.text()])
                                for ciclo in range(comandos[0][5]):
                                    print("Ciclo",ciclo+1)
                                    if ToSave:
                                        w.writerow(["Ciclo "+str(ciclo+1)])
                                        w.writerow(["h (mm)", "v (mm/s)", "a (mm/s2)", "\alpha (graus)","Atraso (s)"])
                                    for comando in comandos:
                                        self.DBManager.WriteOnDB([comando[0],comando[1],comando[2],comando[3]])
                                        self.Table_Historico.clear()
                                        self.InsertDataInTable_Historio()
                                        self.Label_8.setText("Posição atual\n"+str(comando[0])+"mm")
                                        self.Label_9.setText("Inclinação atual\n"+str(comando[1])+"°")
                                        self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                        if ToSave: w.writerow([comando[0],comando[1],comando[2],comando[3],comando[4]])
                                if ToSave:
                                    # Pedir Observação
                                    observacao, done = QInputDialog.getText(self, 'Obs', 'Insira uma observação (opcional):')
                                    # Salvar comandos e observação em CSV
                                    w.writerow(["Observacao",observacao])
                                    f.close()
                            else:
                                QMessageBox.warning(self, 'Aviso', 'Não há nada registrado nessa macro.')
                    self.MacroRunning = False
                else:
                    QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'GravarMacro':
            senha, done = QInputDialog.getText(self, 'Gravar macro', 'Senha:',QLineEdit.Password)
            if done:
                if senha == self.Senha:
                    self.ClearPage()
                    self.GravarMacro = "Gravar"
                    self.CreatePageMain()
                else:
                    QMessageBox.warning(self, 'Erro', 'Senha incorreta.')

        elif ButtonPressed == 'DeletarMacro':
            senha, done = QInputDialog.getText(self, 'Deletar macro', 'Senha:',QLineEdit.Password)
            if done:
                if senha == self.Senha:
                    MacroNames = self.DBManager.GetMacroNames()
                    MacroEscolhida, done = QInputDialog.getItem(self, 'Deletar Macro', 'Macro a ser zerada:', MacroNames, editable=False)
                    if done:
                        IDX = MacroNames.index(MacroEscolhida)
                        NomeJaExiste = list(filter(lambda IdxNome: IdxNome[1] == "Macro"+str(IDX+1) and not IdxNome[0] == IDX, enumerate(self.DBManager.GetMacroNames())))
                        if not NomeJaExiste:
                            self.DBManager.OverwriteMacro(IDX, [])
                            self.DBManager.SetMacroName(IDX, "Macro"+str(IDX+1))

                            MacroNames = self.DBManager.GetMacroNames()
                            self.Button_Macro1.setText(MacroNames[0])
                            self.Button_Macro2.setText(MacroNames[1])
                            self.Button_Macro3.setText(MacroNames[2])
                            self.Button_Macro4.setText(MacroNames[3])
                            self.Button_Macro5.setText(MacroNames[4])
                            self.Button_Macro6.setText(MacroNames[5])
                            self.Button_Macro7.setText(MacroNames[6])
                            self.Button_Macro8.setText(MacroNames[7])
                        else:
                            QMessageBox.warning(self, 'Erro', 'Existe outra macro com o nome que essa deveria receber\n(Macro'+str(IDX+1)+')')
                else:
                    QMessageBox.warning(self, 'Erro', 'Senha incorreta.')

        elif ButtonPressed == 'MaisAceleracao':
            self.AbortThread = False
            self.Thread_MaisAceleracao = WorkerThread('Thread_MaisAceleracao', self)
            self.Thread_MaisAceleracao.start()

        elif ButtonPressed == 'MenosAceleracao':
            self.AbortThread = False
            self.Thread_MenosAceleracao = WorkerThread('Thread_MenosAceleracao', self)
            self.Thread_MenosAceleracao.start()

        elif ButtonPressed == 'MaisVelocidade':
            self.AbortThread = False
            self.Thread_MaisVelocidade = WorkerThread('Thread_MaisVelocidade', self)
            self.Thread_MaisVelocidade.start()

        elif ButtonPressed == 'MenosVelocidade':
            self.AbortThread = False
            self.Thread_MenosVelocidade = WorkerThread('Thread_MenosVelocidade', self)
            self.Thread_MenosVelocidade.start()

        elif ButtonPressed == 'MaisPosicao':
            self.AbortThread = False
            self.Thread_MaisPosicao = WorkerThread('Thread_MaisPosicao', self)
            self.Thread_MaisPosicao.start()

        elif ButtonPressed == 'MenosPosicao':
            self.AbortThread = False
            self.Thread_MenosPosicao = WorkerThread('Thread_MenosPosicao', self)
            self.Thread_MenosPosicao.start()

        elif ButtonPressed == 'MaisInclinacao':
            self.AbortThread = False
            self.Thread_MaisInclinacao = WorkerThread('Thread_MaisInclinacao', self)
            self.Thread_MaisInclinacao.start()

        elif ButtonPressed == 'MenosInclinacao':
            self.AbortThread = False
            self.Thread_MenosInclinacao = WorkerThread('Thread_MenosInclinacao', self)
            self.Thread_MenosInclinacao.start()

        elif ButtonPressed == 'MaxAceleracao':
            self.Aceleracao = self.MaxAceleracao
            self.TextBox_Aceleracao.setText(str(self.Aceleracao))

        elif ButtonPressed == 'MedAceleracao':
            self.Aceleracao = round((self.MaxAceleracao + self.MinAceleracao) / 2,1)
            self.TextBox_Aceleracao.setText(str(self.Aceleracao))

        elif ButtonPressed == 'MinAceleracao':
            self.Aceleracao = self.MinAceleracao
            self.TextBox_Aceleracao.setText(str(self.Aceleracao))

        elif ButtonPressed == 'MaxVelocidade':
            self.Velocidade = self.MaxVelocidade
            self.TextBox_Velocidade.setText(str(self.Velocidade))

        elif ButtonPressed == 'MedVelocidade':
            self.Velocidade = round((self.MaxVelocidade + self.MinVelocidade) / 2,1)
            self.TextBox_Velocidade.setText(str(self.Velocidade))

        elif ButtonPressed == 'MinVelocidade':
            self.Velocidade = self.MinVelocidade
            self.TextBox_Velocidade.setText(str(self.Velocidade))

        elif ButtonPressed == 'MaxPosicao':
            self.Posicao = self.MaxPosicao
            self.TextBox_Posicao.setText(str(self.Posicao))

        elif ButtonPressed == 'MedPosicao':
            self.Posicao = round((self.MaxPosicao + self.MinPosicao) / 2,1)
            self.TextBox_Posicao.setText(str(self.Posicao))

        elif ButtonPressed == 'MinPosicao':
            self.Posicao = self.MinPosicao
            self.TextBox_Posicao.setText(str(self.Posicao))

        elif ButtonPressed == 'MaxInclinacao':
            self.Inclinacao = self.MaxInclinacao
            self.TextBox_Inclinacao.setText(str(self.Inclinacao))

        elif ButtonPressed == 'MedInclinacao':
            self.Inclinacao = round((self.MaxInclinacao + self.MinInclinacao) / 2,1)
            self.TextBox_Inclinacao.setText(str(self.Inclinacao))

        elif ButtonPressed == 'MinInclinacao':
            self.Inclinacao = self.MinInclinacao
            self.TextBox_Inclinacao.setText(str(self.Inclinacao))

        elif ButtonPressed == 'Executar':
            if self.ArduinoComm.Connected:
                sucesso = self.ArduinoComm.SendCommand([self.Posicao, self.Velocidade, self.Aceleracao, self.Inclinacao, 0])
                if sucesso:
                    self.DBManager.WriteOnDB([self.Posicao, self.Velocidade, self.Aceleracao, self.Inclinacao])
                    self.Table_Historico.clear()
                    self.InsertDataInTable_Historio()
                    self.Label_8.setText("Posição atual\n"+str(self.Posicao)+"mm")
                    self.Label_9.setText("Inclinação atual\n"+str(self.Inclinacao)+"°")
            else:
                QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == 'LimparDB':
            MessageBox_Msg1 = QMessageBox()
            MessageBox_Msg1.setWindowTitle("Limpar DB")
            MessageBox_Msg1.setText("Tem certeza que deseja\nlimpar o histórico de comandos?")
            MessageBox_Msg1.setIcon(QMessageBox.Warning)
            MessageBox_Msg1.setStandardButtons(QMessageBox.Yes|QMessageBox.Cancel)
            MessageBox_Msg1.setDefaultButton(QMessageBox.Cancel)
            MessageBox_Msg1.setWindowIcon(QIcon(".\images\Dambreak IHM icon.png"))

            returnValue = MessageBox_Msg1.exec()
            if returnValue == QMessageBox.Yes:
                self.DBManager.ClearDB()
                self.Table_Historico.clear()

        elif ButtonPressed == "ComboBox_Macros":
            IDX = self.ComboBox_Macros.currentIndex()
            NovoNome = self.ComboBox_Macros.currentText()
            if len(NovoNome)<11:
                NomeJaExiste = list(filter(lambda nome: nome == NovoNome, self.DBManager.GetMacroNames()))
                if not NomeJaExiste:
                    self.DBManager.SetMacroName(IDX, NovoNome)

            self.ComboBox_Macros.clear()
            for MacroName in self.DBManager.GetMacroNames():
                self.ComboBox_Macros.addItem(MacroName)
            self.ComboBox_Macros.setCurrentIndex(IDX)

        elif ButtonPressed == "DeletarAcao":
            self.dataMacro = self.dataMacro[::-1]
            self.dataMacro = self.dataMacro[:-1]
            self.dataMacro = self.dataMacro[::-1]

            self.Table_Macro.setRowCount(len(self.dataMacro))

            for i, item in enumerate(self.dataMacro):
                for j in range(len(item)):
                    if not j == 6:
                        it = self.Table_Macro.item(i, j)
                        text = str(item[j])
                        it = QTableWidgetItem(text)
                        if not j == 4:
                            it.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable)) # Desabilita selecionar o item
                            it.setFlags(it.flags() & ~Qt.ItemIsEditable) # Desabilita a edição do item
                        it.setTextAlignment(Qt.AlignCenter)
                        it.setForeground(QBrush(QColor('black')))
                        self.Table_Macro.setItem(i, j, it)
            self.Table_Macro.adjustSize()
            for i in range(5):
                self.Table_Macro.setColumnWidth(i, int(self.frameGeometry().width()*2/7/5))

        elif ButtonPressed == "RegistrarAcao":
            LastMove = self.DBManager.GetAllMoves()
            if len(LastMove)>0:
                LastMove = LastMove[-1]
                self.dataMacro = self.dataMacro[::-1]
                self.dataMacro.append((LastMove[0],LastMove[1],LastMove[2],LastMove[3],1.,int(self.TextBox_Ciclos.text().replace(" ciclos",""))))
                self.dataMacro = self.dataMacro[::-1]

                self.Table_Macro.setRowCount(len(self.dataMacro))

                for i, item in enumerate(self.dataMacro):
                    for j in range(len(item)):
                        if not j == 6:
                            it = self.Table_Macro.item(i, j)
                            text = str(item[j])
                            it = QTableWidgetItem(text)
                            if not j == 4:
                                it.setFlags(Qt.ItemFlags(Qt.ItemIsSelectable)) # Desabilita selecionar o item
                                it.setFlags(it.flags() & ~Qt.ItemIsEditable) # Desabilita a edição do item
                            it.setTextAlignment(Qt.AlignCenter)
                            it.setForeground(QBrush(QColor('black')))
                            self.Table_Macro.setItem(i, j, it)
                self.Table_Macro.adjustSize()
                for i in range(5):
                    self.Table_Macro.setColumnWidth(i, int(self.frameGeometry().width()*2/7/5))

            else:
                QMessageBox.warning(self, 'Aviso', 'Não há comando para registrar.')

        elif ButtonPressed == "TestarMacro":
            if self.ArduinoComm.Connected:
                comandos = self.dataMacro[::-1]
                if len(comandos)>0:
                    for ciclo in range(comandos[0][5]):
                        print("Ciclo",ciclo+1)
                        for comando in comandos:
                            sleep(comando[4])
                            self.ArduinoComm.SendCommand([comando[0],comando[1],comando[2],comando[3],0])
            else:
                QMessageBox.warning(self, 'Erro', 'Arduino não conectado.')

        elif ButtonPressed == "CancelarMacro":
            self.ClearPage()
            self.GravarMacro = "normal"
            self.CreatePageMain()

        elif ButtonPressed == "RegistrarMacro":
            comandos = self.dataMacro
            self.DBManager.OverwriteMacro(self.ComboBox_Macros.currentIndex(), comandos)

            IDX = self.ComboBox_Macros.currentIndex() # Roda isso de novo no caso o usuário não deu enter para renomear a macro
            NovoNome = self.ComboBox_Macros.currentText()
            if len(NovoNome)<11:
                self.DBManager.SetMacroName(IDX, NovoNome)

            self.ClearPage()
            self.GravarMacro = "normal"
            self.CreatePageMain()

        elif ButtonPressed == "ArduinoConnect":
            if sys.platform.startswith('win'):
                ports = ['COM%s' % (i + 1) for i in range(256)]
            elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                # this excludes your current terminal "/dev/tty"
                ports = glob.glob('/dev/tty[A-Za-z]*')
            elif sys.platform.startswith('darwin'):
                ports = glob.glob('/dev/tty.*')
            else:
                raise EnvironmentError('Unsupported platform')

            Ports = []
            for port in ports:
                try:
                    s = serial.Serial(port)
                    s.close()
                    Ports.append(port)
                except (OSError, serial.SerialException):
                    pass
                
            if len(Ports) > 0:
                port, done = QInputDialog.getItem(self, 'Porta', 'Porta onde se encontra o Arduino:', Ports, editable=False)
                if done:
                    self.ArduinoComm.Connect(port)
                    if self.ArduinoComm.Connected == False:
                        QMessageBox.warning(self, 'Erro', 'Impossível se conectar ao arduino.')
                    else:
                        # Save in DB last port used
                        self.DBManager.UpdateCache_Port(port)
            else:
                QMessageBox.warning(self, 'Erro', 'Nenhuma porta serial detectada.')

    def OnButtonReleased(self, ButtonReleased):
            self.AbortThread = True

    def Checkbox_ChangedState(self, precisao):
        if precisao == "1":
            self.Precisao = "1"
            self.PrecisaoAceleracao = 0.1 # (mm/s²)
            self.PrecisaoVelocidade = 0.1 # (mm/s)
            self.PrecisaoPosicao = 0.1 # (mm)
        elif precisao == "1/2":
            self.Precisao = "1/2"
            self.PrecisaoAceleracao = 0.1 # (mm/s²)
            self.PrecisaoVelocidade = 0.1 # (mm/s)
            self.PrecisaoPosicao = 0.1 # (mm)
        elif precisao == "1/4":
            self.Precisao = "1/4"
            self.PrecisaoAceleracao = 0.1 # (mm/s²)
            self.PrecisaoVelocidade = 0.1 # (mm/s)
            self.PrecisaoPosicao = 0.1 # (mm)
        elif precisao == "1/8":
            self.Precisao = "1/8"
            self.PrecisaoAceleracao = 0.1 # (mm/s²)
            self.PrecisaoVelocidade = 0.1 # (mm/s)
            self.PrecisaoPosicao = 0.1 # (mm)
        elif precisao == "1/16":
            self.Precisao = "1/16"
            self.PrecisaoAceleracao = 0.1 # (mm/s²)
            self.PrecisaoVelocidade = 0.1 # (mm/s)
            self.PrecisaoPosicao = 0.1 # (mm)
        elif precisao == "1/32":
            self.Precisao = "1/32"
            self.PrecisaoAceleracao = 0.1 # (mm/s²)
            self.PrecisaoVelocidade = 0.1 # (mm/s)
            self.PrecisaoPosicao = 0.1 # (mm)
        self.DBManager.UpdateCache_Precisao(self.Precisao)

    def OnValueChanged_Aceleracao(self, text):
        def closest(lst, K):
            return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

        if float(self.TextBox_Aceleracao.text().replace("mm/s²","")) <= self.MaxAceleracao and float(self.TextBox_Aceleracao.text().replace("mm/s²","")) >= self.MinAceleracao:
            self.Aceleracao = round(float(self.TextBox_Aceleracao.text().replace("mm/s²","")), 1)
        else:
            self.Aceleracao = round(closest([self.MinAceleracao, self.MaxAceleracao], float(self.TextBox_Aceleracao.text().replace("mm/s²",""))), 1)
            self.TextBox_Aceleracao.setText(str(self.Aceleracao))

        self.DBManager.UpdateCache_Aceleracao(self.Aceleracao)

    def OnValueChanged_Velocidade(self, text):
        def closest(lst, K):
            return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

        if float(self.TextBox_Velocidade.text().replace("mm/s","")) <= self.MaxVelocidade and float(self.TextBox_Velocidade.text().replace("mm/s","")) >= self.MinVelocidade:
            self.Velocidade = round(float(self.TextBox_Velocidade.text().replace("mm/s","")), 1)
        else:
            self.Velocidade = round(closest([self.MinVelocidade, self.MaxVelocidade], float(self.TextBox_Velocidade.text().replace("mm/s",""))), 1)
            self.TextBox_Velocidade.setText(str(self.Velocidade))

        self.DBManager.UpdateCache_Velocidade(self.Velocidade)

    def OnValueChanged_Posicao(self, text):
        def closest(lst, K):
            return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

        if float(self.TextBox_Posicao.text().replace("mm","")) <= self.MaxPosicao and float(self.TextBox_Posicao.text().replace("mm","")) >= self.MinPosicao:
            self.Posicao = round(float(self.TextBox_Posicao.text().replace("mm","")), 1)
        else:
            self.Posicao = round(closest([self.MinPosicao, self.MaxPosicao], float(self.TextBox_Posicao.text().replace("mm",""))), 1)
            self.TextBox_Posicao.setText(str(self.Posicao))

        self.DBManager.UpdateCache_Posicao(self.Posicao)

    def OnValueChanged_Inclinacao(self, text):
        def closest(lst, K):
            return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

        if float(self.TextBox_Inclinacao.text().replace("°","")) <= self.MaxInclinacao and float(self.TextBox_Inclinacao.text().replace("°","")) >= self.MinInclinacao:
            self.Inclinacao = round(float(self.TextBox_Inclinacao.text().replace("°","")), 1)
        else:
            self.Inclinacao = round(closest([self.MinInclinacao, self.MaxInclinacao], float(self.TextBox_Inclinacao.text().replace("°",""))), 1)
            self.TextBox_Inclinacao.setText(str(self.Inclinacao))

        self.DBManager.UpdateCache_Inclinacao(self.Inclinacao)

    def OnValueChanged_Ciclos(self, text):
        try:
            if int(self.TextBox_Ciclos.text().replace(" ciclos","")) >= 0:
                self.Ciclos = int(self.TextBox_Ciclos.text().replace(" ciclos",""))
            else:
                self.Ciclos = 1
                self.TextBox_Ciclos.setText(str(self.Ciclos))
        except:
            self.Ciclos = 1
        finally:
            self.dataMacro = self.dataMacro[::-1]
            for idx, comando in enumerate(self.dataMacro):
                self.dataMacro[idx] = (self.dataMacro[idx][0],self.dataMacro[idx][1],self.dataMacro[idx][2],self.dataMacro[idx][3],self.dataMacro[idx][4],self.Ciclos)
            self.dataMacro = self.dataMacro[::-1]

#%% Resizing HMI
    def eventFilter(self, obj, event): # Função pra redimensionar alguns elementos do IHM dinamicamente
        if event.type() == QEvent.Resize:
            self.Label_10.setFixedHeight(int(self.screen_height/30))
            self.Label_11.setFixedHeight(int(self.screen_height/30))
            self.Button_Tema.setFixedWidth(int(self.screen_width/15))
            self.Button_Macro1.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
            self.Button_Macro2.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
            self.Button_Macro3.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
            self.Button_Macro4.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
            self.Button_Macro5.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
            self.Button_Macro6.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
            self.Button_Macro7.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
            self.Button_Macro8.setFixedSize(int(self.frameGeometry().height()*1/7),int(self.frameGeometry().height()*1/7))
            self.Button_GravarMacro.setFixedHeight(int(self.screen_height/15))
            self.Button_GravarMacro.setFixedWidth(int(self.frameGeometry().height()/7))
            self.Button_DeletarMacro.setFixedHeight(int(self.screen_height/15))
            self.Button_DeletarMacro.setFixedWidth(int(self.frameGeometry().height()/7))
            self.Button_Executar.setFixedWidth(int(self.frameGeometry().width()/3))
            self.TextBox_Aceleracao.setFixedWidth(int(self.frameGeometry().width()/10))
            self.TextBox_Velocidade.setFixedWidth(int(self.frameGeometry().width()/10))
            self.TextBox_Posicao.setFixedWidth(int(self.frameGeometry().width()/10))
            self.TextBox_Inclinacao.setFixedWidth(int(self.frameGeometry().width()/10))
            self.Table_Historico.setFixedWidth(int(self.frameGeometry().width()*0.3))

            self.Button_DeletarAcao.setFixedWidth(int(self.frameGeometry().width()/7))
            self.Button_RegistrarAcao.setFixedWidth(int(self.frameGeometry().width()/7))
            self.Button_TestarMacro.setFixedWidth(int(self.frameGeometry().width()/7))
            self.Button_RegistrarMacro.setFixedWidth(int(self.frameGeometry().width()/7))
            self.Button_CancelarMacro.setFixedWidth(int(self.frameGeometry().width()/7))
            self.TextBox_Ciclos.setFixedWidth(int(self.frameGeometry().width()/7))
            self.ComboBox_Macros.setFixedWidth(int(self.frameGeometry().width()*2/7))
            self.Table_Macro.setFixedWidth(int(self.frameGeometry().width()*2/7))

            for i in range(5):
                self.Table_Macro.setColumnWidth(i, int(self.frameGeometry().width()*2/7/5))

        return False
#%% Keyboard listener
    def tableOnkeyReleaseEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            linha = self.dataMacro[self.Table_Macro.currentIndex().row()]
            linha = (linha[0],linha[1],linha[2],linha[3],float(self.Table_Macro.currentItem().text()))
            self.dataMacro[self.Table_Macro.currentIndex().row()] = linha

#%% App starter
class graphical_thread():
    def __init__(self,):
        self.mIHM = None
        self.app = None

    def run(self,):
        self.app = QApplication(sys.argv)
        self.app.setStyle("fusion")
        try:
            self.mIHM = IHMmain()
            self.app.exec_()
            self.mIHM.ArduinoComm.Close()
            self.mIHM.DBManager.Disconnect()
        except Exception as error:
            print('Erro crítico: \n',error)
            self.mIHM.ArduinoComm.Close()
            self.mIHM.DBManager.Disconnect()
            self.app.quit()
            sys.exit()
            QCoreApplication.quit()

mgraphical_thread = graphical_thread() # Debug
mgraphical_thread.run() # Debug
