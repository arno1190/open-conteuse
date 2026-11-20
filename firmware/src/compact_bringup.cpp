// SPDX-License-Identifier: GPL-3.0-or-later
// Current custom-board diagnostics. Deliberately cannot enable either audio output.
#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <WiFi.h>
#include "card_id.h"
#include "controls.h"
#include "library.h" // SDK compile coverage; SD loader remains an inactive prototype.
#include <Adafruit_ILI9341.h>

namespace {
using namespace board;
constexpr uint8_t Io=IoAddress, Codec=CodecAddress;
#ifdef CONTEUSE_MINI
constexpr int CardPin=Card;
card::Filter cards;
void low(){digitalWrite(CardPin,LOW);pinMode(CardPin,OUTPUT);}
void release(){pinMode(CardPin,INPUT);}
bool resetCard(){noInterrupts();low();delayMicroseconds(480);release();delayMicroseconds(70);bool yes=!digitalRead(CardPin);delayMicroseconds(410);interrupts();return yes;}
void writeSlot(bool b){noInterrupts();low();delayMicroseconds(b?6:60);release();delayMicroseconds(b?64:10);interrupts();}
bool readSlot(){noInterrupts();low();delayMicroseconds(3);release();delayMicroseconds(5);bool b=digitalRead(CardPin);delayMicroseconds(62);interrupts();return b;}
bool readCard(card::Rom& r){if(!resetCard())return false;for(unsigned i=0;i<8;i++)writeSlot((0x33>>i)&1);for(auto& b:r){b=0;for(unsigned i=0;i<8;i++)b|=uint8_t(readSlot())<<i;}return card::valid(r);}

#else
Adafruit_ILI9341 display(LcdCs,LcdDc,LcdReset);
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
#ifdef CONTEUSE_MINI
controls::Decoder inputs(controls::Model::Mini);
#else
controls::Decoder inputs(controls::Model::Explore);
#endif
uint32_t lastPoll=0;
uint8_t previous=0xff;
}
void setup() {
    // Request is LOW before every other peripheral operation. No command raises it.
    digitalWrite(SpeakerRequest,LOW);pinMode(SpeakerRequest,OUTPUT);
    digitalWrite(CodecReset,LOW);pinMode(CodecReset,OUTPUT);
    digitalWrite(LatchClear,LOW);pinMode(LatchClear,OUTPUT);
    pinMode(LatchState,INPUT);pinMode(CodecIrq,INPUT_PULLDOWN);
    digitalWrite(StatusLed,LOW);pinMode(StatusLed,OUTPUT);
    Serial.begin(115200);WiFi.persistent(false);WiFi.mode(WIFI_OFF);
    Wire.begin(I2cSda,I2cScl);Wire.setTimeOut(20);
    bool io=writeReg(Io,3,0xff)&&writeReg(Io,2,0x00);
    delay(10);digitalWrite(CodecReset,HIGH);delay(10);
    // Fresh hardware/software reset keeps all DAC/HP/Class-D paths powered down.
    bool codec=writeReg(Codec,0,0)&&writeReg(Codec,1,1);delay(10);
    codec=codec&&writeReg(Codec,0,0)&&writeReg(Codec,64,0x0c);
    // Leave async /CLR asserted. Audio event/detection register bring-up is separate.
    SPI.begin(SpiClock,SpiMiso,SpiMosi,SdCs);pinMode(LcdCs,OUTPUT);digitalWrite(LcdCs,HIGH);
#ifdef CONTEUSE_MINI
    release(); // External 4.3k pull-up; GPIO9 is unconnected.
#endif
    bool sd=SD.begin(SdCs,SPI,1000000);
#ifdef CONTEUSE_MINI
    Serial.println("Contact ID DS2401 on GPIO8; IDs are selectors, not authentication");
#else
    // Off until SPI panel reset/init completes; PWM limited for first visual test.
    pinMode(Backlight,OUTPUT);digitalWrite(Backlight,LOW);
    display.begin(10000000);display.setRotation(1);display.fillScreen(ILI9341_BLACK);
    display.setTextColor(ILI9341_WHITE);display.setTextSize(2);display.setCursor(10,16);
    display.println("Galia Explore");display.println("MUTED diagnostics");
    ledcSetup(0,2000,8);ledcAttachPin(Backlight,0);ledcWrite(0,32);
#endif
    Serial.printf("RFQ IO=%d CODEC=%d SD=%d PSRAM=%u; audio locked LOW; WiFi OFF\n",io,codec,sd,ESP.getPsramSize());
}
void loop() {
    digitalWrite(SpeakerRequest,LOW);
    if(millis()-lastPoll<50)return;
    lastPoll=millis();
#ifdef CONTEUSE_MINI
    card::Rom id{};bool ok=readCard(id);if(cards.sample(ok?&id:nullptr)){
      Serial.print(cards.present?"CARD ":"CARD removed");
      if(cards.present)for(auto b:cards.active)Serial.printf("%02X",b);
      Serial.println();
    }
#endif
    uint8_t keys=0xff;
    if(!readReg(Io,0,keys)){
        inputs.invalidate(millis());
        previous=0xff;
        digitalWrite(StatusLed,LOW);
        return;
    }
    if(keys!=previous){Serial.printf("Keys active-low=0x%02x; latch=%d\n",keys,digitalRead(LatchState));previous=keys;}
    auto action=inputs.update(uint8_t(~keys),millis(),controls::Mode::Paused);
    if(action!=controls::Action::None)Serial.printf("UX action=%s (muted diagnostic only)\n",controls::name(action));
    digitalWrite(StatusLed,keys!=0xff);
}
