// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <SD.h>
#include <mbedtls/sha256.h>
#include "content.h"
namespace conteuse {
inline std::string fileHash(File& file) {
    mbedtls_sha256_context ctx;mbedtls_sha256_init(&ctx);
    if(mbedtls_sha256_starts_ret(&ctx,0)) {mbedtls_sha256_free(&ctx);return "";}
    uint8_t buffer[512],digest[32];int count;
    while((count=file.read(buffer,sizeof(buffer)))>0) {
        if(mbedtls_sha256_update_ret(&ctx,buffer,count)) {mbedtls_sha256_free(&ctx);return "";}
        delay(0);
    }
    if(count<0) {mbedtls_sha256_free(&ctx);return "";}
    int result=mbedtls_sha256_finish_ret(&ctx,digest);mbedtls_sha256_free(&ctx);
    if(result)return "";
    char hex[65];for(unsigned i=0;i<32;++i)sprintf(hex+2*i,"%02x",digest[i]);
    return std::string(hex,64);
}
inline bool loadRevision(const std::string& revision,Content& output,std::string& directory,
                         const std::string& root="/library/versions/") {
    if(!digestValid(revision))return false;
    std::string base=root+revision+"/";
    File manifest=SD.open((base+"manifest.json").c_str(),FILE_READ);
    if(!manifest||!manifest.size()||manifest.size()>16384||fileHash(manifest)!=revision)return false;
    if(!manifest.seek(0))return false;
    std::string raw;raw.reserve(manifest.size());
    while(manifest.available()) {
        int byte=manifest.read();if(byte<0)return false;
        raw.push_back(static_cast<char>(byte));
    }
    Content candidate;
    if(!parseContent(raw,candidate))return false;
    for(const auto& asset:candidate.assets) {
        File file=SD.open((base+asset.path).c_str(),FILE_READ);
        if(!file||file.size()!=asset.bytes||fileHash(file)!=asset.sha)return false;
    }
    candidate.revision=revision;output=std::move(candidate);directory=base;return true;
}
inline bool loadPointer(const char* pointer,Content& output,std::string& directory) {
    File active=SD.open(pointer,FILE_READ);
    if(!active||active.size()>128)return false;
    StaticJsonDocument<256> doc;
    if(deserializeJson(doc,active)||!nonempty(doc["revision"]))return false;
    return loadRevision(doc["revision"].as<const char*>(),output,directory);
}
inline bool loadLibrary(Content& output,std::string& directory) {
    return loadPointer("/library/active.json",output,directory)||loadPointer("/library/previous.json",output,directory);
}
}
