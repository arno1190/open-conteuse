// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <stdint.h>
#include <stddef.h>
#include <cstring>
namespace conteuse {
struct WavInfo { uint32_t rate=0, bytes=0, offset=0; uint16_t channels=0; };
inline uint16_t le16(const uint8_t* p) { return p[0] | uint16_t(p[1])<<8; }
inline uint32_t le32(const uint8_t* p) { return le16(p) | uint32_t(le16(p+2))<<16; }
// Narrow canonical PCM WAV bench format. Reject other layouts explicitly.
inline bool wavHeader(const uint8_t* h, size_t size, WavInfo& info) {
    if(size < 44 || std::memcmp(h,"RIFF",4) || std::memcmp(h+8,"WAVEfmt ",8)
       || le32(h+16)!=16 || le16(h+20)!=1 || le16(h+34)!=16 || std::memcmp(h+36,"data",4)) return false;
    uint16_t channels=le16(h+22);uint32_t rate=le32(h+24),bytes=le32(h+40);
    if((channels!=1 && channels!=2) || (rate!=16000 && rate!=22050 && rate!=44100)
       || !bytes || bytes>32*1024*1024 || bytes%(channels*2) || le16(h+32)!=channels*2
       || le32(h+28)!=rate*channels*2 || le32(h+4)!=bytes+36) return false;
    info.rate=rate;info.bytes=bytes;info.offset=44;info.channels=channels;return true;
}
}
