// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "card_id.h"
#include <string>
namespace admin {
inline bool bodyExpired(uint32_t now, uint32_t started) {
  return uint32_t(now - started) >= 10000;
}
constexpr size_t JsonBodyLimit = 40000, ChunkBodyLimit = 8192;
inline bool bodyAllowed(size_t length, bool chunk) {
  return length <= (chunk ? ChunkBodyLimit : JsonBodyLimit);
}
constexpr unsigned ChunkBytes = 4096;
constexpr uint32_t MaxAsset = 32u * 1024 * 1024, MaxTotal = 128u * 1024 * 1024;
inline std::string uid(const card::Rom &rom) {
  const char *hex = "0123456789ABCDEF";
  std::string out;
  for (auto b : rom) {
    out += hex[b >> 4];
    out += hex[b & 15];
  }
  return out;
}
inline bool uidValid(const std::string &text) {
  if (text.size() != 16)
    return false;
  card::Rom rom{};
  for (unsigned i = 0; i < 16; ++i) {
    char c = text[i];
    int v = c >= '0' && c <= '9'   ? c - '0'
            : c >= 'A' && c <= 'F' ? c - 'A' + 10
                                   : -1;
    if (v < 0)
      return false;
    rom[i / 2] |= v << ((i % 2) ? 0 : 4);
  }
  return card::valid(rom);
}
inline bool equal(const std::string &a, const std::string &b) {
  if (a.size() != b.size())
    return false;
  unsigned diff = 0;
  for (unsigned i = 0; i < a.size(); ++i)
    diff |= unsigned(a[i] ^ b[i]);
  return diff == 0;
}
inline int base64Value(char c) {
  if (c >= 'A' && c <= 'Z')
    return c - 'A';
  if (c >= 'a' && c <= 'z')
    return c - 'a' + 26;
  if (c >= '0' && c <= '9')
    return c - '0' + 52;
  if (c == '+')
    return 62;
  if (c == '/')
    return 63;
  return -1;
}
inline bool decode64(const std::string &text, std::string &output) {
  output.clear();
  if (text.empty() || text.size() % 4 ||
      text.size() > ((ChunkBytes + 2) / 3) * 4)
    return false;
  for (size_t i = 0; i < text.size(); i += 4) {
    int a = base64Value(text[i]), b = base64Value(text[i + 1]);
    bool p = text[i + 2] == '=', q = text[i + 3] == '=';
    int c = p ? 0 : base64Value(text[i + 2]),
        d = q ? 0 : base64Value(text[i + 3]);
    if (a < 0 || b < 0 || c < 0 || d < 0 || (p && !q) ||
        ((p || q) && i + 4 != text.size()) || (p && (b & 15)) ||
        (q && !p && (c & 3)))
      return false;
    output += char((a << 2) | (b >> 4));
    if (!p)
      output += char((b << 4) | (c >> 2));
    if (!q)
      output += char((c << 6) | d);
  }
  return output.size() <= ChunkBytes;
}
} // namespace admin
