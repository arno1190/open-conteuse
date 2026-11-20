#include "include/controls.h"
#include <cassert>
#include <limits>
using namespace controls;
int main() {
    assert(route(Model::Mini,Mode::Playing,A|Plus)==Action::Pause);
    assert(route(Model::Mini,Mode::Paused,A|Plus)==Action::None);
    assert(route(Model::Mini,Mode::Playing,Left)==Action::PreviousTrack);
    assert(route(Model::Mini,Mode::Choice,Right)==Action::NextChoice);
    assert(route(Model::Explore,Mode::Library,Left)==Action::PreviousPage);
    assert(route(Model::Explore,Mode::Library,Down)==Action::NextItem);
    assert(route(Model::Explore,Mode::Paused,Up)==Action::None);
    assert(route(Model::Mini,Mode::Paused,B)==Action::None);
    assert(route(Model::Explore,Mode::Paused,B)==Action::Back);
    assert(route(Model::Mini,Mode::Busy,A)==Action::Pause);
    assert(route(Model::Mini,Mode::Busy,A|Plus)==Action::Pause);
    assert(route(Model::Explore,Mode::Busy,B)==Action::Back);
    assert(route(Model::Mini,Mode::Paused,Plus|Minus)==Action::None);
    assert(route(Model::Mini,Mode::ChoicePlaying,A|Plus)==Action::Pause);
    assert(route(Model::Mini,Mode::ChoicePaused,A)==Action::Resume);
    assert(route(Model::Mini,Mode::ChoicePlaying,Right)==Action::NextChoice);
    assert(route(Model::Mini,Mode::Ended,A)==Action::Restart);
    assert(route(Model::Mini,Mode::NoCard,A)==Action::HelpMissingSelection);
    Decoder d(Model::Mini);
    assert(d.update(A,0,Mode::Playing)==Action::None);
    assert(d.update(A,30,Mode::Playing)==Action::None); // boot-held: release required
    d.update(0,31,Mode::Playing); d.update(0,56,Mode::Playing);
    d.update(A,60,Mode::Playing);assert(d.update(A,84,Mode::Playing)==Action::None);
    assert(d.update(A,85,Mode::Playing)==Action::Pause);
    assert(d.update(A,1000,Mode::Paused)==Action::None); // never resume on a hold
    d.update(0,1001,Mode::Paused);d.update(0,1026,Mode::Paused);
    d.update(Plus,1030,Mode::Paused);assert(d.update(Plus,1055,Mode::Paused)==Action::VolumeUp);
    assert(d.update(Plus,1654,Mode::Paused)==Action::None);
    assert(d.update(Plus,1655,Mode::Paused)==Action::VolumeUp);
    assert(d.update(Plus,1854,Mode::Paused)==Action::None);
    assert(d.update(Plus,1855,Mode::Paused)==Action::VolumeUp);
    d.update(0,1900,Mode::Paused);d.update(0,1925,Mode::Paused);
    d.update(Right,1930,Mode::Playing);assert(d.update(Right,1955,Mode::Playing)==Action::NextTrack);
    assert(d.update(Right,4000,Mode::Playing)==Action::None);
    Decoder chord(Model::Mini);chord.update(0,0,Mode::Playing);chord.update(0,25,Mode::Playing);
    chord.update(A|Plus,30,Mode::Playing);assert(chord.update(A|Plus,55,Mode::Playing)==Action::Pause);
    chord.update(A,60,Mode::Paused);assert(chord.update(A,85,Mode::Paused)==Action::None);
    assert(chord.update(A,1000,Mode::Paused)==Action::None);
    chord.update(0,1001,Mode::Paused);chord.update(0,1026,Mode::Paused);
    chord.update(A,1030,Mode::Paused);assert(chord.update(A,1055,Mode::Paused)==Action::Resume);
    Decoder ambiguous(Model::Mini);ambiguous.update(0,0,Mode::Paused);ambiguous.update(0,25,Mode::Paused);
    ambiguous.update(Plus|Minus,30,Mode::Paused);assert(ambiguous.update(Plus|Minus,55,Mode::Paused)==Action::None);
    ambiguous.update(Plus,60,Mode::Paused);assert(ambiguous.update(Plus,85,Mode::Paused)==Action::None);
    assert(ambiguous.update(Plus,1000,Mode::Paused)==Action::None);
    ambiguous.update(0,1001,Mode::Paused);ambiguous.update(0,1026,Mode::Paused);
    ambiguous.update(Plus,1030,Mode::Paused);assert(ambiguous.update(Plus,1055,Mode::Paused)==Action::VolumeUp);
    Decoder wrap(Model::Explore);const uint32_t end=std::numeric_limits<uint32_t>::max();
    wrap.update(0,end-50,Mode::Paused);wrap.update(0,end-25,Mode::Paused);
    wrap.update(A,end-10,Mode::Paused);assert(wrap.update(A,15,Mode::Paused)==Action::Resume);
    assert(volumeStep(5,1,5)==5);assert(volumeStep(0,-1,5)==0);
    assert(volumeStep(20,1,255)==20);assert(volumeStep(12,1,4)==4);
    assert(volumeStep(3,1,0)==0);
    Decoder outage(Model::Mini);outage.update(0,0,Mode::Paused);outage.update(0,25,Mode::Paused);
    outage.update(Plus,30,Mode::Paused);assert(outage.update(Plus,55,Mode::Paused)==Action::VolumeUp);
    outage.invalidate(700); // Lost I2C samples must not preserve a repeating hold.
    assert(outage.update(Plus,1000,Mode::Paused)==Action::None);
    assert(outage.update(Plus,2000,Mode::Paused)==Action::None);
    outage.update(0,2010,Mode::Paused);outage.update(0,2035,Mode::Paused);
    outage.update(Plus,2040,Mode::Paused);assert(outage.update(Plus,2065,Mode::Paused)==Action::VolumeUp);
    outage.update(A,2100,Mode::Paused);outage.invalidate(2110);
    assert(outage.update(A,2150,Mode::Paused)==Action::None);
    assert(outage.update(A,2200,Mode::Paused)==Action::None);
    outage.invalidate(3000);
    assert(outage.update(0,5000,Mode::Paused)==Action::None);
    assert(!outage.armed); // Unknown outage time is not observed release time.
    outage.update(0,5024,Mode::Paused);assert(!outage.armed);
    outage.update(0,5025,Mode::Paused);assert(outage.armed);
}
