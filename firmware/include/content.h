// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// Original host-testable validation; no ESPuino code or decoder included.
#include <ArduinoJson.h>
#include <string>
#include <vector>
#include <algorithm>
#include <stdint.h>
#include <cstring>
namespace conteuse {
struct Asset { std::string path,sha; uint32_t bytes; };
struct Choice { std::string label,target; };
struct Node { std::string id,text,audio; std::vector<Choice> choices; };
struct Content { std::string revision,title,start; std::vector<Asset> assets;std::vector<Node> nodes; };
inline bool digestValid(const std::string& value) {
    return value.size()==64 && std::all_of(value.begin(),value.end(),[](char c){return (c>='0'&&c<='9')||(c>='a'&&c<='f');});
}
inline bool pathValid(const std::string& value) {
    if(value.empty() || value.front()=='/' || value.back()=='/')return false;
    size_t from=0;
    while(from<value.size()) {
        size_t end=value.find('/',from);if(end==std::string::npos)end=value.size();
        std::string part=value.substr(from,end-from);
        if(part.empty()||part=="."||part=="..")return false;
        from=end+1;
    }
    for(unsigned char c:value)if(c<32 || c=='\\' || c==':')return false;
    return value!="manifest.json";
}
inline bool stringsValid(JsonVariantConst value) {
    if (!value.isNull() && value.is<const char*>()) {
        JsonString text=value.as<JsonString>();
        if(text.size()!=std::strlen(text.c_str()))return false;
    } else if(value.is<JsonArrayConst>()) {
        for(JsonVariantConst child:value.as<JsonArrayConst>())if(!stringsValid(child))return false;
    } else if(value.is<JsonObjectConst>()) {
        for(JsonPairConst pair:value.as<JsonObjectConst>()) {
            if(pair.key().size()!=std::strlen(pair.key().c_str()) || !stringsValid(pair.value()))return false;
        }
    }
    return true;
}
inline bool nonempty(JsonVariantConst value) {
    if(!value.is<const char*>())return false;
    if(!stringsValid(value))return false;
    const char* s=value.as<const char*>();
    for(;*s;++s)if(*s!=' '&&*s!='\n'&&*s!='\r'&&*s!='\t')return true;
    return false;
}
inline int nodeIndex(const Content& c,const std::string& id) {
    for(size_t i=0;i<c.nodes.size();++i)if(c.nodes[i].id==id)return static_cast<int>(i);
    return -1;
}
// Caller verifies manifest raw canonical-byte digest BEFORE parsing, then every
// asset size/hash before exposing this model. Deliberately tighter device limits.
inline bool parseContent(const std::string& raw,Content& output) {
    if(raw.empty()||raw.size()>16384)return false;
    DynamicJsonDocument doc(98304);
    if(deserializeJson(doc,raw,DeserializationOption::NestingLimit(12)))return false;
    if(!stringsValid(doc.as<JsonVariantConst>()))return false;
    if(!doc.is<JsonObject>() || !doc["format_version"].is<int>() || doc["format_version"].as<int>()!=1
       || !nonempty(doc["id"]) || !nonempty(doc["title"]) || !nonempty(doc["start"]) || !doc["nodes"].is<JsonArray>())return false;
    Content c;c.title=doc["title"].as<const char*>();c.start=doc["start"].as<const char*>();
    JsonArrayConst nodes=doc["nodes"].as<JsonArrayConst>();
    if(!nodes.size()||nodes.size()>128)return false;
    if(doc.containsKey("assets")&&!doc["assets"].is<JsonArray>())return false;
    JsonArrayConst assets=doc["assets"].as<JsonArrayConst>();
    if(assets.size()>64)return false;
    uint64_t total=0;
    for(JsonVariantConst value:assets) {
        if(!value.is<JsonObjectConst>() || !nonempty(value["path"]) || !nonempty(value["sha256"]) || !value["size"].is<uint32_t>())return false;
        Asset a{value["path"].as<const char*>(),value["sha256"].as<const char*>(),value["size"].as<uint32_t>()};
        if(!pathValid(a.path)||!digestValid(a.sha)||!a.bytes||a.bytes>32*1024*1024)return false;
        for(const auto& old:c.assets)if(a.path==old.path)return false;
        total+=a.bytes;if(total>128*1024*1024)return false;
        c.assets.push_back(a);
    }
    for(JsonVariantConst value:nodes) {
        if(!value.is<JsonObjectConst>()||!nonempty(value["id"])||!nonempty(value["text"]))return false;
        Node n;n.id=value["id"].as<const char*>();n.text=value["text"].as<const char*>();
        if(nodeIndex(c,n.id)>=0)return false;
        if(value.as<JsonObjectConst>().containsKey("audio")) {
            if(!nonempty(value["audio"]))return false;
            n.audio=value["audio"].as<const char*>();
            bool found=false;for(const auto& a:c.assets)if(a.path==n.audio)found=true;
            if(!found)return false;
        }
        if(value.as<JsonObjectConst>().containsKey("choices")&&!value["choices"].is<JsonArrayConst>())return false;
        JsonArrayConst choices=value["choices"].as<JsonArrayConst>();
        if(choices.size()>16)return false;
        for(JsonVariantConst choice:choices) {
            if(!choice.is<JsonObjectConst>()||!nonempty(choice["label"])||!nonempty(choice["target"]))return false;
            n.choices.push_back({choice["label"].as<const char*>(),choice["target"].as<const char*>()});
        }
        c.nodes.push_back(n);
    }
    int start=nodeIndex(c,c.start);if(start<0)return false;
    std::vector<bool> seen(c.nodes.size(),false),exits(c.nodes.size(),false);seen[start]=true;
    for(size_t i=0;i<c.nodes.size();++i) {
        exits[i]=c.nodes[i].choices.empty();
        for(const auto& choice:c.nodes[i].choices)if(nodeIndex(c,choice.target)<0)return false;
    }
    // Bounded transitive closure handles cycles without recursive stack growth.
    for(size_t pass=0;pass<c.nodes.size();++pass)for(size_t i=0;i<c.nodes.size();++i)
        for(const auto& choice:c.nodes[i].choices) {
            int target=nodeIndex(c,choice.target);
            if(seen[i])seen[target]=true;
            if(exits[target])exits[i]=true;
        }
    for(size_t i=0;i<c.nodes.size();++i)if(!seen[i]||!exits[i])return false;
    output=std::move(c);return true;
}
}
