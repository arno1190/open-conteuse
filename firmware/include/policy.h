// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <stdint.h>

// Hardware-free policy. No audio decoder or package parser is claimed here.
namespace conteuse {
enum class State { Paused, Playing, Choice, Ended, Buffering, Offline };
struct Policy {
    State state = State::Paused;
    bool headphones = false;
    bool wifi = false;
    uint8_t retries = 0;
    void toggle() { state = state == State::Playing ? State::Paused : State::Playing; }
    void local() { wifi = false; state = State::Paused; }
    bool radio(bool approved) {
        if (!approved) return false;
        wifi = true; retries = 0; state = State::Buffering; return true;
    }
    void failed() {
        if (retries < 3) ++retries;
        state = retries >= 3 ? State::Offline : State::Buffering;
    }
    bool speaker() const { return state == State::Playing && !headphones; }
};
}
