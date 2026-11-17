// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// Optional bench-only direct MP3/AAC streaming, using ESP8266Audio (GPL-3.0-or-later).
#include <Arduino.h>
#include <WiFi.h>
#include <SD.h>
#include <ArduinoJson.h>
#include <AudioFileSourceHTTPStream.h>
#include <AudioFileSourceBuffer.h>
#include <AudioGeneratorMP3.h>
#include <AudioGeneratorAAC.h>
#include <AudioOutputI2S.h>
#include <memory>
namespace conteuse {
class Radio {
    std::unique_ptr<AudioFileSourceHTTPStream> source;
    std::unique_ptr<AudioFileSourceBuffer> buffer;
    std::unique_ptr<AudioGenerator> decoder;
    std::unique_ptr<AudioOutputI2S> output;
    String url,mime;
    uint8_t attempts=0;
    uint32_t started=0,nextAttempt=0;
    bool enabled=false;
    void closeStream() {
        if(decoder)decoder->stop();decoder.reset();buffer.reset();source.reset();output.reset();
    }
    bool connect() {
        ++attempts;
        source.reset(new AudioFileSourceHTTPStream());
        source->SetReconnect(0,0); // total retries belong to this state machine
        // Direct HTTP bench streams only. HTTPS needs an explicit verified-TLS
        // transport adapter; never silently disable certificate validation.
        if(!source->open(url.c_str())) {closeStream();return false;}
        buffer.reset(new AudioFileSourceBuffer(source.get(),8192));
        output.reset(new AudioOutputI2S());output->SetPinout(40,41,42);output->SetGain(0.0625f);
        if(mime=="audio/mpeg")decoder.reset(new AudioGeneratorMP3());
        else decoder.reset(new AudioGeneratorAAC());
        if(!decoder->begin(buffer.get(),output.get())) {closeStream();return false;}
        return true;
    }
public:
    bool active() const { return enabled; }
    bool playing() const { return decoder&&decoder->isRunning(); }
    void stop() {closeStream();enabled=false;WiFi.mode(WIFI_OFF);}
    bool start(const char* station) {
        if(WiFi.status()!=WL_CONNECTED)return false;
        File file=SD.open("/library/stations.json",FILE_READ);StaticJsonDocument<4096> doc;
        if(!file||file.size()>4096||deserializeJson(doc,file))return false;
        JsonObject entry=doc[station];
        if(!entry["approved"].is<bool>()||!entry["approved"].as<bool>()||!entry["url"].is<const char*>()||!entry["mime"].is<const char*>())return false;
        String candidate=entry["url"].as<const char*>(),type=entry["mime"].as<const char*>();
        if(!candidate.startsWith("http://")||candidate.length()>512||candidate.indexOf('@')>=0||candidate.indexOf('#')>=0
           ||(type!="audio/mpeg"&&type!="audio/aac"))return false;
        closeStream();url=candidate;mime=type;attempts=0;started=millis();nextAttempt=millis();enabled=true;
        return true;
    }
    void loop() {
        if(!enabled)return;
        if(uint32_t(millis()-started)>=15*60*1000) {stop();return;}
        if(decoder&&decoder->isRunning()) {
            if(decoder->loop())return;
            closeStream();nextAttempt=millis()+5000;
        }
        if(!decoder && int32_t(millis()-nextAttempt)>=0) {
            if(attempts>=3) {Serial.println("Radio unavailable after three attempts");stop();return;}
            if(!connect())nextAttempt=millis()+5000;
        }
    }
};
}
