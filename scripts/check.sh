#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -v
python3 -m conteuse examples/first-adventure/manifest.json
python3 -m conteuse.demo
c++ -std=c++17 -Wall -Wextra -Werror firmware/card_id_test.cpp -o /tmp/conteuse-card-test
/tmp/conteuse-card-test
python3 content/starter/validate.py
python3 site/check.py
node --check site/app.js
python3 scripts/check_release.py

c++ -std=c++17 -Wall -Wextra -Werror firmware/controls_test.cpp -o /tmp/conteuse-controls-test
/tmp/conteuse-controls-test
