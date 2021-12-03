# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 22:07:06 2021

@author: caiop
"""
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time

class WorkerThread(QThread): # Ainda estou estudando uma maneira de implementar isso
    def __init__(self, ThreadName, HMI):
        super().__init__()
        self.__abort = False
        self.__id = ThreadName
        self.HMI = HMI # Da permissão a todo o controle do HMI

    def run(self):
        if self.__id == 'Thread_MaisAceleracao':
            while not self.HMI.AbortThread:
                if self.HMI.Aceleracao < self.HMI.MaxAceleracao:
                    self.HMI.Aceleracao += self.HMI.PrecisaoAceleracao
                    self.HMI.Aceleracao = round(self.HMI.Aceleracao, 1) # Evita bugs de arredondamentos de double do python
                    self.HMI.TextBox_Aceleracao.setText(str(self.HMI.Aceleracao))
                    time.sleep(0.2)
                else: self.HMI.AbortThread = True

        elif self.__id == 'Thread_MenosAceleracao':
            while not self.HMI.AbortThread:
                if self.HMI.Aceleracao > self.HMI.MinAceleracao:
                    self.HMI.Aceleracao -= self.HMI.PrecisaoAceleracao
                    self.HMI.Aceleracao = round(self.HMI.Aceleracao, 1) # Evita bugs de arredondamentos de double do python
                    self.HMI.TextBox_Aceleracao.setText(str(self.HMI.Aceleracao))
                    time.sleep(0.2)
                else: self.HMI.AbortThread = True

        elif self.__id == 'Thread_MaisVelocidade':
            while not self.HMI.AbortThread:
                if self.HMI.Velocidade < self.HMI.MaxVelocidade:
                    self.HMI.Velocidade += self.HMI.PrecisaoVelocidade
                    self.HMI.Velocidade = round(self.HMI.Velocidade, 1) # Evita bugs de arredondamentos de double do python
                    self.HMI.TextBox_Velocidade.setText(str(self.HMI.Velocidade))
                    time.sleep(0.2)
                else: self.HMI.AbortThread = True

        elif self.__id == 'Thread_MenosVelocidade':
            while not self.HMI.AbortThread:
                if self.HMI.Velocidade > self.HMI.MinVelocidade:
                    self.HMI.Velocidade -= self.HMI.PrecisaoVelocidade
                    self.HMI.Velocidade = round(self.HMI.Velocidade, 1) # Evita bugs de arredondamentos de double do python
                    self.HMI.TextBox_Velocidade.setText(str(self.HMI.Velocidade))
                    time.sleep(0.2)
                else: self.HMI.AbortThread = True

        elif self.__id == 'Thread_MaisPosicao':
            while not self.HMI.AbortThread:
                if self.HMI.Posicao < self.HMI.MaxPosicao:
                    self.HMI.Posicao += self.HMI.PrecisaoPosicao
                    self.HMI.Posicao = round(self.HMI.Posicao, 1) # Evita bugs de arredondamentos de double do python
                    self.HMI.TextBox_Posicao.setText(str(self.HMI.Posicao))
                    time.sleep(0.2)
                else: self.HMI.AbortThread = True

        elif self.__id == 'Thread_MenosPosicao':
            while not self.HMI.AbortThread:
                if self.HMI.Posicao > self.HMI.MinPosicao:
                    self.HMI.Posicao -= self.HMI.PrecisaoPosicao
                    self.HMI.Posicao = round(self.HMI.Posicao, 1) # Evita bugs de arredondamentos de double do python
                    self.HMI.TextBox_Posicao.setText(str(self.HMI.Posicao))
                    time.sleep(0.2)
                else: self.HMI.AbortThread = True

        elif self.__id == 'Thread_MaisInclinacao':
            while not self.HMI.AbortThread:
                if self.HMI.Inclinacao < self.HMI.MaxInclinacao:
                    self.HMI.Inclinacao += self.HMI.PrecisaoInclinacao
                    self.HMI.Inclinacao = round(self.HMI.Inclinacao, 1) # Evita bugs de arredondamentos de double do python
                    self.HMI.TextBox_Inclinacao.setText(str(self.HMI.Inclinacao))
                    time.sleep(0.2)
                else: self.HMI.AbortThread = True

        elif self.__id == 'Thread_MenosInclinacao':
            while not self.HMI.AbortThread:
                if self.HMI.Inclinacao > self.HMI.MinInclinacao:
                    self.HMI.Inclinacao -= self.HMI.PrecisaoInclinacao
                    self.HMI.Inclinacao = round(self.HMI.Inclinacao, 1) # Evita bugs de arredondamentos de double do python
                    self.HMI.TextBox_Inclinacao.setText(str(self.HMI.Inclinacao))
                    time.sleep(0.2)
                else: self.HMI.AbortThread = True