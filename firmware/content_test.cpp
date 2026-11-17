// SPDX-License-Identifier: GPL-3.0-or-later
#include "include/content.h"
#include <cassert>
#include <fstream>
#include <iterator>
int main(int argc,char** argv) {
    assert(argc==2);
    std::ifstream file(argv[1]);std::string raw((std::istreambuf_iterator<char>(file)),{});
    conteuse::Content c;assert(conteuse::parseContent(raw,c));
    assert(c.nodes.size()==3 && c.start=="gate");
    assert(!conteuse::parseContent("[]",c));
    assert(!conteuse::parseContent(std::string(16385,'x'),c));
    std::string cycle=R"({"format_version":1,"id":"x","title":"X","start":"x","nodes":[{"id":"x","text":"loop","choices":[{"label":"again","target":"x"}]}]})";
    assert(!conteuse::parseContent(cycle,c));
    std::string unsafe=R"({"format_version":1,"id":"x","title":"X","start":"x","nodes":[{"id":"x","text":"end"}],"assets":[{"path":"../bad","size":1,"sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}]})";
    assert(!conteuse::parseContent(unsafe,c));
    assert(!conteuse::pathValid("a/../b") && !conteuse::pathValid("a//b"));
    assert(conteuse::pathValid("audio/a.wav"));
}
