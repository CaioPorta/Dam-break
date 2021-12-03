# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 12:20:47 2021

@author: caiop
"""
from time import sleep

from serial import *

class ArduinoComm(object):
    def __init__(self, HMI):
        self.HMI = HMI
        self.Connected = False

    def Connect(self, port):
        # Estabelecer comunicação com arduino
        try:
            self.ArduinoComm = Serial(port, 9600, timeout=1)
            # self.ArduinoComm.write(str.encode('UTF-8'))
            self.Connected = True
        except:
            print("Impossível se conectar ao arduino")
            self.Connected = False

    def SendCommand(self, comando):
        if self.Connected:
            # Verificar se o comando não é duplicado # Antibug
            LastMove = self.HMI.DBManager.GetAllMoves()
            if len(LastMove)>0:
                LastMove = LastMove[-1]
                if (comando[0] == LastMove[0] and
                    comando[1] == LastMove[1] and
                    comando[2] == LastMove[2] and
                    comando[3] == LastMove[3]):
                    return False
            # Enviar comando ao arduino
            sleep(comando[4])
            int_posicao = int(comando[0]*10)
            int_velocidade = int(comando[1]*10)
            int_aceleracao = int(comando[2]*10)
            int_inclinacao = int(comando[3]*10)
            str_posicao = "{:017b}".format(int_posicao)
            str_velocidade = "{:017b}".format(int_velocidade)
            str_aceleracao = "{:017b}".format(int_aceleracao)
            str_inclinacao = "{:017b}".format(int_inclinacao)
            mensagem = str_posicao + str_velocidade + str_aceleracao + str_inclinacao
            print("Enviando comando ao arduino:\n",
                  str("h="+str(comando[0])+"mm | "+
                      "v="+str(comando[1])+"mm/s | "+
                      "a="+str(comando[2])+"mm/s² | "+
                      "\u03B1="+str(comando[3])+"°\n"))
            self.ArduinoComm.write(mensagem.encode('UTF-8'))
            # self.WaitResponse(5)
            return True
        else:
            return False

    def WaitResponse(self, timeout=10):
        if self.Connected:
            resposta = 'timeout'
            ticking = 0
            while ticking < timeout:
                # Procura por array vindo do Arduino
                packet = self.ArduinoComm.readline()
                resposta = sum(byte*(0x100**i) for i, byte in enumerate(packet)) # Convert hex to dec
                print(resposta/10)
                if len(packet) > 0:
                    flush = self.ArduinoComm.readline() # Clear buffer
                    break
                # Se não tiver array, espera um pouco
                ticking += 1
                sleep(1)
            return resposta
        else:
            return None

    def Close(self):
        try: self.ArduinoComm.close()
        except: pass