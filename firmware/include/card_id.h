// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <stdint.h>
#include <array>
namespace card {
using Rom=std::array<uint8_t,8>;
inline uint8_t crc(const uint8_t* bytes,unsigned n){uint8_t c=0;while(n--){uint8_t b=*bytes++;for(int i=0;i<8;i++){bool mix=(c^b)&1;c>>=1;if(mix)c^=0x8c;b>>=1;}}return c;}
inline bool valid(const Rom& r){return r[0]==1&&crc(r.data(),7)==r[7];}
// Three consecutive identical CRC-valid reads to insert; two misses to remove.
// A changed valid ID clears the current selection immediately before debounce.
struct Filter {
 Rom candidate{},active{};unsigned count=0,misses=0;bool present=false;
 bool sample(const Rom* r){
  const bool was=present;const Rom old=active;
  if(!r||!valid(*r)){count=0;if(++misses>=2)present=false;}
  else {misses=0;if(*r!=candidate){candidate=*r;count=1;present=false;}else if(count<3)++count;if(count>=3){active=*r;present=true;}}
  return was!=present||(present&&old!=active);
 }
};
}
