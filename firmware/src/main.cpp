// SPDX-License-Identifier: GPL-3.0-or-later
#include <Arduino.h>
#include <WiFi.h>
#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include <Adafruit_PN532.h>
#include <Adafruit_ILI9341.h>
#include <driver/i2s.h>
#include "policy.h"
#include "wav.h"
#include "library.h"
#include "radio.h"

// ESP32-S3-DevKitC-1 / ESP32-S3-WROOM-1-N16R8 ONLY.
// No use of OPI35..37, USB19/20, strapping0/3/45/46 or onboard RGB48.
constexpr int Controls[] = {4, 5, 6, 7, 15, 16, 17, 18};
constexpr int HeadphoneDetect = 21, SpeakerEnable = 47, SdCS = 10;
constexpr int I2sBclk = 40, I2sLrclk = 41, I2sData = 42;
Adafruit_PN532 nfc(8,9,&Wire);
#ifdef CONTEUSE_EXPLORE
Adafruit_ILI9341 display(14,38,39);
#endif
conteuse::Policy player;
conteuse::Radio radio;
String command;
conteuse::Button buttons[8];
File audio;
conteuse::WavInfo wav;
uint32_t remaining=0, lastCard=0;
bool nfcReady=false, i2sReady=false, libraryReady=false;
conteuse::Content content;
std::string contentDirectory;
int currentNode=0;
unsigned selectedChoice=0;
std::vector<int> history;
void renderNode() {
    if(!libraryReady)return;
    const auto& node=content.nodes[currentNode];
    Serial.println(node.text.c_str());
    for(size_t i=0;i<node.choices.size();++i)Serial.printf("%u: %s\n",unsigned(i),node.choices[i].label.c_str());
#ifdef CONTEUSE_EXPLORE
    display.fillRect(0,80,320,160,ILI9341_BLACK);display.setCursor(8,80);
    display.println(node.text.c_str());
    for(size_t i=0;i<node.choices.size();++i) {
        display.print(i==selectedChoice?"> ":"  ");display.println(node.choices[i].label.c_str());
    }
#endif
}
void finishNode() {
    player.state=libraryReady&&!content.nodes[currentNode].choices.empty()?conteuse::State::Choice:conteuse::State::Ended;
    renderNode();
}

// This is a compile-time bench opt-in after a wiring review, never enabled in CI.
#ifndef CONTEUSE_BENCH_AUDIO
#define CONTEUSE_BENCH_AUDIO 0
#endif

void stopAudio() {
    digitalWrite(SpeakerEnable,LOW);
    audio.close();remaining=0;player.state=conteuse::State::Paused;
    if(i2sReady) i2s_zero_dma_buffer(I2S_NUM_0);
}

void initI2s();

bool startAudio(const char* path="/bench.wav") {
    radio.stop();
    stopAudio();
    initI2s();
    if(!CONTEUSE_BENCH_AUDIO || !i2sReady) { Serial.println("Bench audio disabled");return false; }
    // This fixed bench fixture is NOT a published pack or remotely writable path.
    audio=SD.open(path,FILE_READ);
    uint8_t header[44];
    if(!audio || audio.read(header,44)!=44 || !conteuse::wavHeader(header,44,wav)
       || audio.size()!=wav.bytes+44) { stopAudio();Serial.println("Unsupported/missing PCM bench.wav");return false; }
    if(i2s_set_clk(I2S_NUM_0,wav.rate,I2S_BITS_PER_SAMPLE_16BIT,I2S_CHANNEL_STEREO)!=ESP_OK) {stopAudio();return false;}
    remaining=wav.bytes;player.state=conteuse::State::Playing;
    return true;
}

void initI2s() {
    if(i2sReady)return;
    if(CONTEUSE_BENCH_AUDIO) {
        i2s_config_t config={};config.mode=i2s_mode_t(I2S_MODE_MASTER|I2S_MODE_TX);
        config.sample_rate=16000;config.bits_per_sample=I2S_BITS_PER_SAMPLE_16BIT;
        config.channel_format=I2S_CHANNEL_FMT_RIGHT_LEFT;config.communication_format=I2S_COMM_FORMAT_STAND_I2S;
        config.intr_alloc_flags=0;config.dma_buf_count=4;config.dma_buf_len=128;config.tx_desc_auto_clear=true;
        i2s_pin_config_t pins={};pins.bck_io_num=I2sBclk;pins.ws_io_num=I2sLrclk;
        pins.data_out_num=I2sData;pins.data_in_num=I2S_PIN_NO_CHANGE;pins.mck_io_num=I2S_PIN_NO_CHANGE;
        if(i2s_driver_install(I2S_NUM_0,&config,0,nullptr)==ESP_OK) {
            i2sReady=i2s_set_pin(I2S_NUM_0,&pins)==ESP_OK;
            if(!i2sReady)i2s_driver_uninstall(I2S_NUM_0);
        }
    }
}

void setup() {
    pinMode(SpeakerEnable,OUTPUT);digitalWrite(SpeakerEnable,LOW);
    pinMode(HeadphoneDetect,INPUT_PULLUP);
    for(int pin:Controls)pinMode(pin,INPUT_PULLUP);
    Serial.begin(115200);WiFi.persistent(false);WiFi.mode(WIFI_OFF);
    SPI.begin(12,13,11,SdCS);
    pinMode(14,OUTPUT);digitalWrite(14,HIGH); // deselect TFT on shared SPI
    const bool mounted=SD.begin(SdCS,SPI,1000000);
    Wire.begin(1,2);Wire.setTimeOut(20);
    nfc.begin();nfcReady=nfc.getFirmwareVersion()!=0;
    if(nfcReady) { nfc.SAMConfig();nfc.setPassiveActivationRetries(1); }
#ifdef CONTEUSE_EXPLORE
    display.begin(10000000);display.setRotation(1);display.fillScreen(ILI9341_BLACK);
    display.setTextColor(ILI9341_WHITE);display.setTextSize(2);display.setCursor(8,12);
    display.println("Open Conteuse");display.println("Explore bench");
    display.println(mounted?"SD ready":"SD missing");display.println(nfcReady?"NFC ready":"NFC missing");
    display.println("Wi-Fi off");
#endif
    initI2s();
    if(mounted)libraryReady=conteuse::loadLibrary(content,contentDirectory);
    if(libraryReady) {currentNode=conteuse::nodeIndex(content,content.start);renderNode();}
    Serial.printf("SD=%d NFC=%d PACK=%d PSRAM=%u bytes AUDIO_OPT_IN=%d\n",mounted,nfcReady,libraryReady,ESP.getPsramSize(),CONTEUSE_BENCH_AUDIO);
}

void serialCommands() {
    while(Serial.available()) {
        char ch=static_cast<char>(Serial.read());
        if(ch=='\n') {
            if(CONTEUSE_BENCH_AUDIO && command.startsWith("wifi ")) {
                int split=command.indexOf('\t',5);
                if(split>5) {stopAudio();radio.stop();WiFi.mode(WIFI_STA);WiFi.begin(command.substring(5,split).c_str(),command.substring(split+1).c_str());}
            } else if(CONTEUSE_BENCH_AUDIO && command.startsWith("radio ")) {
                stopAudio();
                if(i2sReady) {i2s_driver_uninstall(I2S_NUM_0);i2sReady=false;}
                if(!radio.start(command.substring(6).c_str()))Serial.println("Station unavailable or unapproved (direct HTTP MP3/AAC only)");
            } else if(command=="stop") {radio.stop();stopAudio();}
            // No command echo: Wi-Fi passwords must never be logged.
            command="";
        } else if(ch!='\r') {
            if(command.length()<256)command+=ch;
            else command="";
        }
    }
}

void loop() {
    serialCommands();
    radio.loop();
    // An external amplifier pulldown and independent jack switch remain required.
    player.headphones=digitalRead(HeadphoneDetect)==LOW;
    if(player.headphones)digitalWrite(SpeakerEnable,LOW);
    for(unsigned i=0;i<8;++i)if(buttons[i].update(digitalRead(Controls[i])==LOW,millis())) {
        Serial.printf("button %u\n",i);
        if(i==1) {
            radio.stop();
            if(audio)stopAudio();
            else if(libraryReady) {
                const auto& node=content.nodes[currentNode];
                if(player.state==conteuse::State::Choice && !node.choices.empty()) {
                    if(history.size()==128)history.erase(history.begin());
                    history.push_back(currentNode);
                    currentNode=conteuse::nodeIndex(content,node.choices[selectedChoice].target);selectedChoice=0;
                }
                const auto& next=content.nodes[currentNode];
                renderNode();
                if(next.audio.empty())finishNode();
                else startAudio((contentDirectory+next.audio).c_str());
            } else startAudio();
        }
        if(libraryReady && (i==3||i==4)) {
            const size_t count=content.nodes[currentNode].choices.size();
            if(count) {selectedChoice=(selectedChoice+count+(i==3?-1:1))%count;renderNode();}
        }
        if(libraryReady && i==5 && !history.empty()) {
            stopAudio();currentNode=history.back();history.pop_back();selectedChoice=0;renderNode();
        }
#ifdef CONTEUSE_EXPLORE
        display.fillRect(8,180,224,30,ILI9341_BLACK);display.setCursor(8,180);display.printf("Button %u",i);
#endif
    }
    if(audio && remaining && player.state==conteuse::State::Playing) {
        int16_t input[128],output[256];
        const size_t wanted=remaining<sizeof(input)?remaining:sizeof(input);
        int got=audio.read(reinterpret_cast<uint8_t*>(input),wanted);
        if(got<=0 || got%(wav.channels*2)) {stopAudio();return;}
        remaining-=got;
        const int samples=got/2;
        // Fixed 1/16 digital gain for bench signal tracing, not an acoustic limit.
        for(int i=0;i<samples;++i) {
            if(wav.channels==1)output[2*i]=output[2*i+1]=input[i]/16;
            else output[i]=input[i]/16;
        }
        size_t sent=0,bytes=wav.channels==1?got*2:got;
        if(i2s_write(I2S_NUM_0,output,bytes,&sent,pdMS_TO_TICKS(20))!=ESP_OK || sent!=bytes) {stopAudio();return;}
        digitalWrite(SpeakerEnable,CONTEUSE_BENCH_AUDIO && player.speaker() ? HIGH : LOW);
        if(!remaining) {stopAudio();finishNode();}
    }
    // Poll NFC only while stopped; synchronous PN532 transactions must not stall audio.
    if(nfcReady && !audio && !radio.active() && uint32_t(millis()-lastCard)>250) {
        lastCard=millis();uint8_t uid[7],length=0;
        if(nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A,uid,&length,20)) {
            char card[15]={0};for(unsigned i=0;i<length;++i)sprintf(card+2*i,"%02x",uid[i]);
            File assignments=SD.open("/library/cards.json",FILE_READ);
            StaticJsonDocument<4096> cards;
            bool known=libraryReady&&assignments&&assignments.size()<=4096&&!deserializeJson(cards,assignments)
                && cards[card].is<const char*>() && content.revision==cards[card].as<const char*>();
            if(known) {radio.stop();currentNode=conteuse::nodeIndex(content,content.start);history.clear();selectedChoice=0;player.local();renderNode();}
            else Serial.printf("Unassigned card: %s\n",card);
        }
    }
    if(radio.active())digitalWrite(SpeakerEnable,CONTEUSE_BENCH_AUDIO && radio.playing() && !player.headphones?HIGH:LOW);
    else if(!audio)digitalWrite(SpeakerEnable,LOW);
    delay(1);
}
