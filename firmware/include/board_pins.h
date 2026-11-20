// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <stdint.h>
// Current custom boards. scripts/check_board_contracts.py binds these names to
// the ESP32-S3-WROOM pad map, component contracts and native PCB pad nets.
namespace board {
constexpr int I2cSda=1, I2cScl=2;
constexpr int CodecReset=4, LatchClear=5, LatchState=6, Card=8;
constexpr int SdCs=10, SpiMosi=11, SpiClock=12, SpiMiso=13;
constexpr int LcdCs=14, LcdDc=38, LcdReset=9, Backlight=8;
constexpr int SpeakerRequest=47, StatusLed=48, CodecIrq=21;
constexpr uint8_t IoAddress=0x20, CodecAddress=0x18;
enum Key : uint8_t { Up=1, A=2, Down=4, Left=8, Right=16, B=32, Minus=64, Plus=128 };
}
