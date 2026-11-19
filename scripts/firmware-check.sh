#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p work
PIO="${PIO:-pio}"
"$PIO" run -d firmware -e mini -e explore -e mini-bench-audio -e explore-bench-audio -e compact-mini-bringup -e compact-explore-bringup
c++ -std=c++17 -Wall -Wextra -Werror firmware/policy_test.cpp -o work/policy-test
work/policy-test
c++ -std=c++17 -Wall -Wextra -Werror -Ifirmware/.pio/libdeps/mini/ArduinoJson/src firmware/content_test.cpp -o work/content-test
work/content-test examples/first-adventure/manifest.json
