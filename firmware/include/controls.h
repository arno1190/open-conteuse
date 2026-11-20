// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <stdint.h>

namespace controls {
// TCA9534 active-high pressed mask after inversion of the hardware register.
enum Key : uint8_t { Up=1, A=2, Down=4, Left=8, Right=16, B=32, Minus=64, Plus=128 };
enum class Model { Mini, Explore };
enum class Mode { NoCard, Library, Playing, Paused, Choice, ChoicePlaying, ChoicePaused, Ended, Busy };
enum class Action {
    None, Pause, Resume, Restart, HelpMissingSelection, Select, Back, PreviousTrack, NextTrack,
    PreviousChoice, NextChoice, PreviousItem, NextItem, PreviousPage, NextPage,
    VolumeDown, VolumeUp
};

inline bool audioPlaying(Mode mode) { return mode==Mode::Playing || mode==Mode::ChoicePlaying; }

inline Action route(Model model, Mode mode, uint8_t keys) {
    if (model==Model::Mini) keys &= uint8_t(A|Left|Right|Minus|Plus);
    if (!keys) return Action::None;
    // Pausing wins over clumsy multi-button presses. A combination never resumes.
    if ((audioPlaying(mode) || mode==Mode::Busy) && (keys&A)) return Action::Pause;
    if (keys & uint8_t(keys-1)) return Action::None;
    if (keys==Minus) return Action::VolumeDown;
    if (keys==Plus) return Action::VolumeUp;
    if (mode==Mode::NoCard) return keys==A ? Action::HelpMissingSelection : Action::None;
    if (keys==B) return model==Model::Explore ? Action::Back : Action::None;
    if (mode==Mode::Busy) return Action::None;
    if (keys==A) return mode==Mode::Ended ? Action::Restart : (mode==Mode::Paused || mode==Mode::ChoicePaused) ? Action::Resume : Action::Select;
    if (mode==Mode::Choice || mode==Mode::ChoicePlaying || mode==Mode::ChoicePaused) {
        if (keys==Left || keys==Up) return Action::PreviousChoice;
        if (keys==Right || keys==Down) return Action::NextChoice;
    } else if (mode==Mode::Library) {
        if (keys==Up) return Action::PreviousItem;
        if (keys==Down) return Action::NextItem;
        if (keys==Left) return model==Model::Mini ? Action::PreviousItem : Action::PreviousPage;
        if (keys==Right) return model==Model::Mini ? Action::NextItem : Action::NextPage;
    } else if (mode==Mode::Playing || mode==Mode::Paused || mode==Mode::Ended) {
        if (keys==Left) return Action::PreviousTrack;
        if (keys==Right) return Action::NextTrack;
    }
    return Action::None;
}

inline const char* name(Action a) {
    switch (a) {
    case Action::None: return "none";
    case Action::Pause: return "pause";
    case Action::Resume: return "resume";
    case Action::Restart: return "restart selection";
    case Action::HelpMissingSelection: return "help: missing selection";
    case Action::Select: return "confirm selection";
    case Action::Back: return "back";
    case Action::PreviousTrack: return "previous track";
    case Action::NextTrack: return "next track";
    case Action::PreviousChoice: return "previous choice";
    case Action::NextChoice: return "next choice";
    case Action::PreviousItem: return "previous item";
    case Action::NextItem: return "next item";
    case Action::PreviousPage: return "previous page";
    case Action::NextPage: return "next page";
    case Action::VolumeDown: return "volume down";
    case Action::VolumeUp: return "volume up";
    }
    return "unknown";
}

struct Decoder {
    Model model;
    uint8_t candidate=0, stable=0;
    uint32_t changed=0, pressedAt=0, repeatAt=0;
    bool armed=false, chord=false;
    explicit Decoder(Model value):model(value) {}
    Action update(uint8_t pressed, uint32_t now, Mode mode) {
        if (model==Model::Mini) pressed &= uint8_t(A|Left|Right|Minus|Plus);
        if (pressed!=candidate) { candidate=pressed; changed=now; }
        if (uint32_t(now-changed)<25) return Action::None;
        if (!armed) { if (!candidate) armed=true; stable=candidate; return Action::None; }
        if (candidate!=stable) {
            const uint8_t rising=uint8_t(candidate & uint8_t(~stable));
            stable=candidate; pressedAt=repeatAt=now;
            if (!stable) { chord=false; return Action::None; }
            if (stable & uint8_t(stable-1)) {
                chord=true;
                return (audioPlaying(mode) || mode==Mode::Busy) && (rising&A) ? Action::Pause : Action::None;
            }
            // Releasing part of a chord cannot become a fresh press or a repeat.
            if (chord || !rising) return Action::None;
            return route(model,mode,stable);
        }
        if (!chord && (stable==Minus || stable==Plus) && uint32_t(now-pressedAt)>=600 && uint32_t(now-repeatAt)>=200) {
            repeatAt=now;
            return route(model,mode,stable);
        }
        return Action::None;
    }
};

// Logical limit only. Absolute loudness needs measured acoustic calibration.
inline uint8_t volumeStep(uint8_t current, int delta, uint8_t parentLimit) {
    const int limit=parentLimit>20 ? 20 : parentLimit;
    int value=current>limit ? limit : current;
    value+=delta<0 ? -1 : delta>0 ? 1 : 0;
    return uint8_t(value<0 ? 0 : value>limit ? limit : value);
}
}
