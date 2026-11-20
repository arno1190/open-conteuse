// SPDX-License-Identifier: GPL-3.0-or-later
#include "include/policy.h"
#include "include/wav.h"
#include <cassert>
#include <cstdint>
int main() {
    uint8_t h[44]={};
    std::memcpy(h,"RIFF",4);std::memcpy(h+8,"WAVEfmt ",8);std::memcpy(h+36,"data",4);
    auto put16=[&](int i,uint16_t v){h[i]=v;h[i+1]=v>>8;};
    auto put32=[&](int i,uint32_t v){put16(i,v);put16(i+2,v>>16);};
    put32(4,68);put32(16,16);put16(20,1);put16(22,1);put32(24,16000);
    put32(28,32000);put16(32,2);put16(34,16);put32(40,32);
    conteuse::WavInfo w;
    assert(conteuse::wavHeader(h,44,w) && w.rate==16000 && w.bytes==32);
    put32(40,33);assert(!conteuse::wavHeader(h,44,w));
    put32(40,32);put16(20,3);assert(!conteuse::wavHeader(h,44,w));
    assert(!conteuse::wavHeader(h,12,w));
    conteuse::Policy p;
    assert(!p.speaker() && !p.wifi);
    p.toggle(); assert(p.speaker());
    p.headphones = true; assert(!p.speaker());
    assert(!p.radio(false) && !p.wifi);
    assert(p.radio(true) && p.wifi);
    p.failed(); p.failed(); assert(p.state == conteuse::State::Buffering);
    p.failed(); p.failed(); assert(p.state == conteuse::State::Offline);
    p.local(); assert(!p.wifi && !p.speaker());
}
