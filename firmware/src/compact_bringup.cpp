// SPDX-License-Identifier: GPL-3.0-or-later
// Compact R1 diagnostics. Deliberately cannot enable either audio output.
#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <WiFi.h>
#include <Adafruit_PN532.h>
#include <Adafruit_ILI9341.h>

namespace {
constexpr uint8_t Io=0x20, Codec=0x18;
constexpr int SpeakerRequest=47, CodecReset=4, LatchClear=5, LatchState=6;
#ifdef CONTEUSE_MINI
Adafruit_PN532 nfc(8,&SPI);
#else
Adafruit_ILI9341 display(14,38,9);
#endif
bool writeReg(uint8_t address,uint8_t reg,uint8_t value) {
    Wire.beginTransmission(address);Wire.write(reg);Wire.write(value);
    return Wire.endTransmission()==0;
}
bool readReg(uint8_t address,uint8_t reg,uint8_t& value) {
    Wire.beginTransmission(address);Wire.write(reg);
    if(Wire.endTransmission(false)!=0)return false;
    if(Wire.requestFrom(address,uint8_t(1))!=1)return false;
    value=Wire.read();return true;
}
uint32_t lastPoll=0;
uint8_t previous=0xff;
}
void setup() {
    // Request is LOW before every other peripheral operation. No command raises it.
    digitalWrite(SpeakerRequest,LOW);pinMode(SpeakerRequest,OUTPUT);
    digitalWrite(CodecReset,LOW);pinMode(CodecReset,OUTPUT);
    digitalWrite(LatchClear,LOW);pinMode(LatchClear,OUTPUT);
    pinMode(LatchState,INPUT);pinMode(21,INPUT_PULLDOWN);
    digitalWrite(48,LOW);pinMode(48,OUTPUT);
    Serial.begin(115200);WiFi.persistent(false);WiFi.mode(WIFI_OFF);
    Wire.begin(1,2);Wire.setTimeOut(20);
    bool io=writeReg(Io,3,0xff)&&writeReg(Io,2,0x00);
    delay(10);digitalWrite(CodecReset,HIGH);delay(10);
    // Fresh hardware/software reset keeps all DAC/HP/Class-D paths powered down.
    bool codec=writeReg(Codec,0,0)&&writeReg(Codec,1,1);delay(10);
    codec=codec&&writeReg(Codec,0,0)&&writeReg(Codec,64,0x0c);
    // Leave async /CLR asserted. Audio event/detection register bring-up is separate.
    SPI.begin(12,13,11,10);pinMode(14,OUTPUT);digitalWrite(14,HIGH);
#ifdef CONTEUSE_MINI
    pinMode(8,OUTPUT);digitalWrite(8,HIGH);
    pinMode(9,OUTPUT);digitalWrite(9,LOW);delay(10);digitalWrite(9,HIGH);delay(10);
#endif
    bool sd=SD.begin(10,SPI,1000000);
#ifdef CONTEUSE_MINI
    nfc.begin();bool nfcOk=nfc.getFirmwareVersion()!=0;
    if(nfcOk){nfc.SAMConfig();nfc.setPassiveActivationRetries(1);}
    Serial.printf("PN532 SPI=%d\n",nfcOk);
#else
    // Off until SPI panel reset/init completes; PWM limited for first visual test.
    pinMode(8,OUTPUT);digitalWrite(8,LOW);
    display.begin(10000000);display.setRotation(1);display.fillScreen(ILI9341_BLACK);
    display.setTextColor(ILI9341_WHITE);display.setTextSize(2);display.setCursor(10,16);
    display.println("Compact Explore R1");display.println("MUTED diagnostics");
    ledcSetup(0,2000,8);ledcAttachPin(8,0);ledcWrite(0,32);
#endif
    Serial.printf("CompactR1 IO=%d CODEC=%d SD=%d PSRAM=%u; audio locked LOW; WiFi OFF\n",io,codec,sd,ESP.getPsramSize());
}
void loop() {
    digitalWrite(SpeakerRequest,LOW);
    if(millis()-lastPoll<50)return;
    lastPoll=millis();uint8_t keys=0xff;
    if(!readReg(Io,0,keys)){digitalWrite(48,LOW);return;}
    if(keys!=previous){Serial.printf("Keys active-low=0x%02x; latch=%d\n",keys,digitalRead(LatchState));previous=keys;}
    digitalWrite(48,keys!=0xff);
}
