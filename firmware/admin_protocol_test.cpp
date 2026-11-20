#include "include/card_mapping.h"
#include <cassert>
#include <fstream>
#include <iterator>
#include <map>
struct FakeStore {
  std::map<std::string, std::string> files;
  bool shortWrite = false, corruptWrite = false, failRemove = false,
       failRename = false;
  std::string read(const std::string &p) { return files[p]; }
  bool write(const std::string &p, const std::string &bytes) {
    files[p] = bytes;
    if (shortWrite || corruptWrite)
      files[p].resize(bytes.size() / 2);
    return !shortWrite;
  }
  bool remove(const std::string &p) {
    if (failRemove)
      return false;
    files.erase(p);
    return true;
  }
  bool rename(const std::string &a, const std::string &b) {
    if (failRename)
      return false;
    files[b] = files[a];
    files.erase(a);
    return true;
  }
};
std::string testHash(const std::string &value) {
  uint32_t h = 2166136261u;
  for (unsigned char c : value)
    h = (h ^ c) * 16777619u;
  std::string out(64, '0');
  for (int i = 0; i < 8; ++i)
    out[63 - i] = "0123456789abcdef"[(h >> (i * 4)) & 15];
  return out;
}
int main(int argc, char **argv) {
  if (argc == 6) {
    std::ifstream file(argv[1]);
    std::string raw((std::istreambuf_iterator<char>(file)), {});
    std::string uid = argv[2], revision = argv[3], generation = argv[4],
                expected = argv[5];
    auto hash = [&](const std::string &input) {
      assert(input == uid + ":" + revision + ":" + generation);
      return expected;
    };
    auto record = admin::decodeMapping(raw, uid, 0, hash);
    assert(record.revision == revision &&
           std::to_string(record.generation) == generation);
    return 0;
  }
  assert(argc == 1);
  card::Rom r{{1, 2, 3, 4, 5, 6, 7, 0}};
  r[7] = card::crc(r.data(), 7);
  auto id = admin::uid(r);
  assert(admin::uidValid(id));
  assert(!admin::uidValid("not-an-id"));
  assert(!admin::uidValid("0102030405060700"));
  assert(admin::equal(id, id));
  assert(!admin::equal(id, id + "0"));
  assert(admin::ChunkBytes == 4096);
  std::string bytes;
  assert(admin::decode64(
      "AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1"
      "Njc4OTo7PD0+"
      "P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0"
      "dXZ3eHl6e3x9fn+"
      "AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+"
      "wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/"
      "g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==",
      bytes));
  assert(bytes.size() == 256);
  for (unsigned i = 0; i < 256; ++i)
    assert(static_cast<unsigned char>(bytes[i]) == i);
  assert(admin::decode64("AA==", bytes) && bytes == std::string(1, '\0'));
  for (const auto &invalid :
       {"", "A===", "AB==", "AAF=", "AA==AAAA", "!!!!", "AA=Z", "A"})
    assert(!admin::decode64(invalid, bytes));
  assert(!admin::decode64(std::string(5468, 'A'), bytes));
  assert(admin::bodyAllowed(8192, true));
  assert(!admin::bodyAllowed(8193, true));
  assert(!admin::bodyAllowed(SIZE_MAX, false));
  assert(!admin::bodyAllowed(40001, false));
  assert(!admin::bodyExpired(9999, 0));
  assert(admin::bodyExpired(10000, 0));
  assert(admin::bodyExpired(4999, UINT32_MAX - 5000));
  FakeStore store;
  std::string first(64, 'a'), second(64, 'b');
  assert(admin::writeMapping(store, id, first, testHash));
  assert(admin::readMapping(store, id, testHash).revision == first);
  std::string deep = "[]";
  for (int i = 0; i < 12; ++i)
    deep = "[" + deep + "]";
  for (const auto &extra : {std::string(",\"extra\":\"bad\\u0000value\""),
                            ",\"extra\":{\"deep\":" + deep + "}"}) {
    FakeStore parity = store;
    assert(admin::writeMapping(parity, id, second, testHash));
    auto active = admin::mappingPath(id, 0), higher = admin::mappingPath(id, 1);
    const auto old = parity.files[active];
    auto raw = parity.files[higher];
    raw.pop_back();
    parity.files[higher] = raw + extra + "}";
    StaticJsonDocument<2048> fixture;
    assert(!deserializeJson(fixture, parity.files[higher],
                            DeserializationOption::NestingLimit(32)));
    assert(admin::readMapping(parity, id, testHash).revision == first);
    assert(admin::writeMapping(parity, id, second, testHash));
    assert(parity.files[active] == old);
  }
  for (const char *suffix : {" ", "garbage"}) {
    FakeStore parity = store;
    assert(admin::writeMapping(parity, id, second, testHash));
    auto active = admin::mappingPath(id, 0), higher = admin::mappingPath(id, 1);
    const auto old = parity.files[active];
    parity.files[higher] += suffix;
    assert(admin::readMapping(parity, id, testHash).revision == first);
    assert(admin::writeMapping(parity, id, second, testHash));
    assert(parity.files[active] == old);
  }
  for (int fault = 0; fault < 4; ++fault) {
    FakeStore damaged = store;
    damaged.shortWrite = fault == 0;
    damaged.corruptWrite = fault == 1;
    damaged.failRemove = fault == 2;
    damaged.failRename = fault == 3;
    assert(!admin::writeMapping(damaged, id, second, testHash));
    auto recovered = admin::readMapping(damaged, id, testHash);
    assert(recovered.revision == first && recovered.generation == 1);
  }
  assert(admin::writeMapping(store, id, second, testHash));
  auto newest = admin::readMapping(store, id, testHash);
  assert(newest.revision == second && newest.generation == 2);
  store.files[admin::mappingPath(id, newest.slot)] =
      "{\"generation\":4294967295,\"revision\":\"" + second +
      "\",\"sha256\":\"bad\"}";
  assert(admin::readMapping(store, id, testHash).revision == first);
  assert(!admin::writeMapping(store, "bad", first, testHash));
}
