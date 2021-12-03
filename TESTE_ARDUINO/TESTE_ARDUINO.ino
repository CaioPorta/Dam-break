char incomingData[68];
float Posicao;
float Velocidade;
float Aceleracao;
float Inclinacao;

float ConvertToNumber_Posicao (char incomingData[68]) {
  float Posicao = 0;
  int Bit = incomingData[16] - '0';
  Posicao = Bit * pow(2,0);
  Bit = incomingData[15] - '0';
  Posicao += Bit * pow(2,1);
  Bit = incomingData[14] - '0';
  Posicao += Bit * pow(2,2);
  Bit = incomingData[13] - '0';
  Posicao += Bit * pow(2,3);
  Bit = incomingData[12] - '0';
  Posicao += Bit * pow(2,4);
  Bit = incomingData[11] - '0';
  Posicao += Bit * pow(2,5);
  Bit = incomingData[10] - '0';
  Posicao += Bit * pow(2,6);
  Bit = incomingData[9] - '0';
  Posicao += Bit * pow(2,7);
  Bit = incomingData[8] - '0';
  Posicao += Bit * pow(2,8);
  Bit = incomingData[7] - '0';
  Posicao += Bit * pow(2,9);
  Bit = incomingData[6] - '0';
  Posicao += Bit * pow(2,10);
  Bit = incomingData[5] - '0';
  Posicao += Bit * pow(2,11);
  Bit = incomingData[4] - '0';
  Posicao += Bit * pow(2,12);
  Bit = incomingData[3] - '0';
  Posicao += Bit * pow(2,13);
  Bit = incomingData[2] - '0';
  Posicao += Bit * pow(2,14);
  Bit = incomingData[1] - '0';
  Posicao += Bit * pow(2,15);
  Bit = incomingData[0] - '0';
  Posicao += Bit * pow(2,16);
  return Posicao/10.; // (mm)
}

float ConvertToNumber_Velocidade (char incomingData[68]) {
  float Velocidade = 0;
  int Bit = incomingData[33] - '0';
  Velocidade = Bit * pow(2,0);
  Bit = incomingData[32] - '0';
  Velocidade += Bit * pow(2,1);
  Bit = incomingData[31] - '0';
  Velocidade += Bit * pow(2,2);
  Bit = incomingData[30] - '0';
  Velocidade += Bit * pow(2,3);
  Bit = incomingData[29] - '0';
  Velocidade += Bit * pow(2,4);
  Bit = incomingData[28] - '0';
  Velocidade += Bit * pow(2,5);
  Bit = incomingData[27] - '0';
  Velocidade += Bit * pow(2,6);
  Bit = incomingData[26] - '0';
  Velocidade += Bit * pow(2,7);
  Bit = incomingData[25] - '0';
  Velocidade += Bit * pow(2,8);
  Bit = incomingData[24] - '0';
  Velocidade += Bit * pow(2,9);
  Bit = incomingData[23] - '0';
  Velocidade += Bit * pow(2,10);
  Bit = incomingData[22] - '0';
  Velocidade += Bit * pow(2,11);
  Bit = incomingData[21] - '0';
  Velocidade += Bit * pow(2,12);
  Bit = incomingData[20] - '0';
  Velocidade += Bit * pow(2,13);
  Bit = incomingData[19] - '0';
  Velocidade += Bit * pow(2,14);
  Bit = incomingData[18] - '0';
  Velocidade += Bit * pow(2,15);
  Bit = incomingData[17] - '0';
  Velocidade += Bit * pow(2,16);
  return Velocidade/10.; // (mm/s)
}

float ConvertToNumber_Aceleracao (char incomingData[68]) {
  float Aceleracao = 0;
  int Bit = incomingData[50] - '0';
  Aceleracao = Bit * pow(2,0);
  Bit = incomingData[49] - '0';
  Aceleracao += Bit * pow(2,1);
  Bit = incomingData[48] - '0';
  Aceleracao += Bit * pow(2,2);
  Bit = incomingData[47] - '0';
  Aceleracao += Bit * pow(2,3);
  Bit = incomingData[46] - '0';
  Aceleracao += Bit * pow(2,4);
  Bit = incomingData[45] - '0';
  Aceleracao += Bit * pow(2,5);
  Bit = incomingData[44] - '0';
  Aceleracao += Bit * pow(2,6);
  Bit = incomingData[43] - '0';
  Aceleracao += Bit * pow(2,7);
  Bit = incomingData[42] - '0';
  Aceleracao += Bit * pow(2,8);
  Bit = incomingData[41] - '0';
  Aceleracao += Bit * pow(2,9);
  Bit = incomingData[40] - '0';
  Aceleracao += Bit * pow(2,10);
  Bit = incomingData[39] - '0';
  Aceleracao += Bit * pow(2,11);
  Bit = incomingData[38] - '0';
  Aceleracao += Bit * pow(2,12);
  Bit = incomingData[37] - '0';
  Aceleracao += Bit * pow(2,13);
  Bit = incomingData[36] - '0';
  Aceleracao += Bit * pow(2,14);
  Bit = incomingData[35] - '0';
  Aceleracao += Bit * pow(2,15);
  Bit = incomingData[34] - '0';
  Aceleracao += Bit * pow(2,16);
  return Aceleracao/10.; // (mm/s²)
}

float ConvertToNumber_Inclinacao (char incomingData[68]) {
  float Inclinacao = 0;
  int Bit = incomingData[67] - '0';
  Inclinacao = Bit * pow(2,0);
  Bit = incomingData[66] - '0';
  Inclinacao += Bit * pow(2,1);
  Bit = incomingData[65] - '0';
  Inclinacao += Bit * pow(2,2);
  Bit = incomingData[64] - '0';
  Inclinacao += Bit * pow(2,3);
  Bit = incomingData[63] - '0';
  Inclinacao += Bit * pow(2,4);
  Bit = incomingData[62] - '0';
  Inclinacao += Bit * pow(2,5);
  Bit = incomingData[61] - '0';
  Inclinacao += Bit * pow(2,6);
  Bit = incomingData[60] - '0';
  Inclinacao += Bit * pow(2,7);
  Bit = incomingData[59] - '0';
  Inclinacao += Bit * pow(2,8);
  Bit = incomingData[58] - '0';
  Inclinacao += Bit * pow(2,9);
  Bit = incomingData[57] - '0';
  Inclinacao += Bit * pow(2,10);
  Bit = incomingData[56] - '0';
  Inclinacao += Bit * pow(2,11);
  Bit = incomingData[55] - '0';
  Inclinacao += Bit * pow(2,12);
  Bit = incomingData[54] - '0';
  Inclinacao += Bit * pow(2,13);
  Bit = incomingData[53] - '0';
  Inclinacao += Bit * pow(2,14);
  Bit = incomingData[52] - '0';
  Inclinacao += Bit * pow(2,15);
  Bit = incomingData[51] - '0';
  Inclinacao += Bit * pow(2,16);
  return Inclinacao/10.; // (°)
}

void setup() {  
  Serial.begin(9600); // initialize serial communication:
}

void loop() {
  if (Serial.available() > 0) { // Wait for data in buffer
    Serial.readBytes(incomingData, 68); // Read data in buffer
    Posicao = ConvertToNumber_Posicao(incomingData); //[0:16]
    Velocidade = ConvertToNumber_Velocidade(incomingData); //[17:33]
    Aceleracao = ConvertToNumber_Aceleracao(incomingData); //[34:50]
    Inclinacao = ConvertToNumber_Inclinacao(incomingData); //[51:67]
    
    //uint32_t pos = Posicao*10;
    //Serial.write((byte *) &pos, 4); // usado por self.ArduinoComm.WaitResponse()
  }
}
