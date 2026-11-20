// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "admin_protocol.h"
#include "bounded_http.h"
#include "card_mapping.h"
#include "library.h"
#include <WiFi.h>
#include <esp_system.h>
#include <esp_wifi.h>
namespace admin {
inline std::string sha(const std::string &value) {
  uint8_t digest[32];
  if (mbedtls_sha256_ret(reinterpret_cast<const uint8_t *>(value.data()),
                         value.size(), digest, 0))
    return "";
  const char *hex = "0123456789abcdef";
  std::string out;
  for (auto b : digest) {
    out += hex[b >> 4];
    out += hex[b & 15];
  }
  return out;
}
inline std::string randomHex(unsigned bytes) {
  std::string raw;
  for (unsigned i = 0; i < bytes; ++i)
    raw += char(esp_random() & 255);
  return sha(raw).substr(0, bytes * 2);
}
inline bool assetPath(const std::string &path) {
  if (path.empty() || path.size() > 120 || !conteuse::pathValid(path) ||
      std::count(path.begin(), path.end(), '/') >= 8)
    return false;
  for (char c : path)
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
          (c >= '0' && c <= '9') || c == '.' || c == '_' || c == '-' ||
          c == '/'))
      return false;
  std::string lower = path;
  std::transform(lower.begin(), lower.end(), lower.begin(),
                 [](char c) { return c >= 'A' && c <= 'Z' ? c + 32 : c; });
  return lower != "manifest.json" && lower.rfind("manifest.json/", 0) != 0;
}
inline bool mkdirs(const std::string &file) {
  for (size_t pos = 1; (pos = file.find('/', pos)) != std::string::npos;
       ++pos) {
    auto dir = file.substr(0, pos);
    if (!SD.exists(dir.c_str()) && !SD.mkdir(dir.c_str()))
      return false;
  }
  return true;
}
inline bool removeTree(const std::string &path) {
  File root = SD.open(path.c_str());
  if (!root)
    return true;
  if (!root.isDirectory()) {
    root.close();
    return SD.remove(path.c_str());
  }
  File child = root.openNextFile();
  while (child) {
    std::string next = path + "/" + child.name();
    child.close();
    if (!removeTree(next))
      return false;
    child = root.openNextFile();
  }
  root.close();
  return SD.rmdir(path.c_str());
}
struct CardFiles {
  std::string read(const std::string &path) {
    File f = SD.open(path.c_str());
    if (!f || f.size() > 512)
      return "";
    std::string out;
    while (f.available()) {
      int b = f.read();
      if (b < 0)
        return "";
      out += char(b);
    }
    return out;
  }
  bool write(const std::string &path, const std::string &raw) {
    if (!mkdirs(path))
      return false;
    SD.remove(path.c_str());
    File f = SD.open(path.c_str(), FILE_WRITE);
    if (!f)
      return false;
    auto n = f.write(reinterpret_cast<const uint8_t *>(raw.data()), raw.size());
    f.flush();
    f.close();
    return n == raw.size();
  }
  bool remove(const std::string &path) {
    return !SD.exists(path.c_str()) || SD.remove(path.c_str());
  }
  bool rename(const std::string &from, const std::string &to) {
    return SD.rename(from.c_str(), to.c_str());
  }
};
inline Mapping mapping(const std::string &id) {
  CardFiles files;
  return readMapping(files, id, sha);
}
inline bool assign(const std::string &id, const std::string &rev) {
  CardFiles files;
  return writeMapping(files, id, rev, sha);
}
// One bounded read per loop; reused by setup verification and offline
// selection.
class PackVerifier {
  File file;
  mbedtls_sha256_context hash;
  bool hashing = false;
  size_t index = 0;
  uint32_t readBytes = 0;

public:
  conteuse::Content content;
  std::string base;
  bool pending = false, valid = false;
  uint64_t completed = 0, total = 0;
  PackVerifier() { mbedtls_sha256_init(&hash); }
  ~PackVerifier() {
    cancel();
    mbedtls_sha256_free(&hash);
  }
  void cancel() {
    file.close();
    pending = valid = false;
    hashing = false;
    content = conteuse::Content{};
    index = 0;
    completed = total = 0;
  }
  bool begin(const std::string &revision,
             const std::string &root = "/library/versions/") {
    cancel();
    if (!conteuse::digestValid(revision))
      return false;
    base = root + revision + "/";
    File manifest = SD.open((base + "manifest.json").c_str());
    if (!manifest || manifest.size() > 16384 || !manifest.size())
      return false;
    std::string raw;
    while (manifest.available()) {
      int b = manifest.read();
      if (b < 0)
        return false;
      raw += char(b);
    }
    manifest.close();
    if (sha(raw) != revision || !conteuse::parseContent(raw, content))
      return false;
    total = completed = raw.size();
    for (const auto &a : content.assets) {
      if (a.bytes > MaxAsset)
        return false;
      total += a.bytes;
    }
    if (total > MaxTotal)
      return false;
    content.revision = revision;
    pending = true;
    return true;
  }
  void step() {
    if (!pending)
      return;
    if (index == content.assets.size()) {
      pending = false;
      valid = true;
      return;
    }
    const auto &asset = content.assets[index];
    if (!hashing) {
      file = SD.open((base + asset.path).c_str());
      if (!file || file.size() != asset.bytes ||
          mbedtls_sha256_starts_ret(&hash, 0)) {
        cancel();
        return;
      }
      readBytes = 0;
      hashing = true;
    }
    uint8_t buffer[ChunkBytes];
    size_t want = std::min<size_t>(ChunkBytes, asset.bytes - readBytes);
    if (want) {
      int n = file.read(buffer, want);
      if (n <= 0 || size_t(n) != want ||
          mbedtls_sha256_update_ret(&hash, buffer, n)) {
        cancel();
        return;
      }
      readBytes += n;
      completed += n;
    }
    if (readBytes == asset.bytes) {
      uint8_t digest[32];
      if (mbedtls_sha256_finish_ret(&hash, digest)) {
        cancel();
        return;
      }
      std::string hex;
      const char *chars = "0123456789abcdef";
      for (auto b : digest) {
        hex += chars[b >> 4];
        hex += chars[b & 15];
      }
      file.close();
      hashing = false;
      if (hex != asset.sha) {
        cancel();
        return;
      }
      ++index;
    }
  }
};
class Server {
  Http web;
  SemaphoreHandle_t mutex = nullptr;
  std::string token, staging, current, jobKind, jobUid, jobState = "idle",
                                                        jobRevision;
  conteuse::Content incoming;
  PackVerifier verifier;
  uint32_t started = 0, lastRequest = 0;
  bool running = false;
  bool auth() {
    if (uint32_t(millis() - started) >= 7200000 ||
        uint32_t(millis() - lastRequest) >= 180000) {
      error("setup session expired", 403);
      return false;
    }
    const String host = web.hostHeader(), origin = web.header("Origin");
    bool ok = (host == "192.168.4.1" || host == "192.168.4.1:80") &&
              (origin.isEmpty() || origin == "http://192.168.4.1") &&
              equal(std::string(web.header("Authorization").c_str()),
                    "Bearer " + token);
    if (!ok) {
      error("unauthorized", 403);
      return false;
    }
    lastRequest = millis();
    return true;
  }
  void error(const char *message, int code = 400) {
    StaticJsonDocument<256> d;
    d["error"] = message;
    String body;
    serializeJson(d, body);
    web.send(code, "application/json", body);
  }
  bool json(DynamicJsonDocument &d) {
    String body = web.arg("plain");
    return body.length() <= JsonBodyLimit && !deserializeJson(d, body) &&
           d.is<JsonObject>() &&
           conteuse::stringsValid(d.as<JsonVariantConst>());
  }
  void reply(JsonDocument &d) {
    String body;
    serializeJson(d, body);
    web.send(200, "application/json", body);
  }
  bool busy() {
    if (jobState == "pending") {
      error("verification in progress", 409);
      return true;
    }
    return false;
  }
  void jobReply() {
    StaticJsonDocument<512> d;
    d["state"] = jobState;
    d["revision"] = jobRevision;
    d["uid"] = jobUid;
    d["verified_bytes"] = verifier.completed;
    d["total_bytes"] = verifier.total;
    reply(d);
  }
  void beginTransfer() {
    if (!auth() || busy())
      return;
    DynamicJsonDocument d(50000);
    if (!json(d) || !conteuse::nonempty(d["revision"]) ||
        !conteuse::nonempty(d["manifest"]))
      return error("invalid request");
    std::string rev = d["revision"].as<const char *>(),
                raw = d["manifest"].as<const char *>();
    conteuse::Content parsed;
    if (!conteuse::digestValid(rev) || sha(raw) != rev ||
        !conteuse::parseContent(raw, parsed))
      return error("invalid manifest/hash");
    uint64_t total = raw.size();
    std::vector<std::string> paths;
    for (const auto &a : parsed.assets) {
      if (!assetPath(a.path) || a.bytes > MaxAsset)
        return error("unsupported asset path/size");
      std::string lower = a.path;
      std::transform(lower.begin(), lower.end(), lower.begin(),
                     [](char c) { return c >= 'A' && c <= 'Z' ? c + 32 : c; });
      for (const auto &p : paths)
        if (p == lower || p.rfind(lower + "/", 0) == 0 ||
            lower.rfind(p + "/", 0) == 0)
          return error("FAT path collision");
      paths.push_back(lower);
      total += a.bytes;
    }
    if (total > MaxTotal)
      return error("pack too large");
    StaticJsonDocument<128> result;
    // Existing bytes are checked by the incremental assignment job, never
    // trusted here.
    if (SD.exists(("/library/versions/" + rev).c_str())) {
      result["existing"] = true;
      return reply(result);
    }
    if (!staging.empty() && !removeTree("/library/incoming/" + staging))
      return error("staging cleanup failed", 500);
    std::string dir = "/library/incoming/" + rev;
    if (!removeTree(dir) || !mkdirs(dir + "/manifest.json"))
      return error("cannot prepare staging", 500);
    if (SD.totalBytes() < SD.usedBytes() ||
        SD.totalBytes() - SD.usedBytes() < total + 16384)
      return error("insufficient storage", 507);
    File f = SD.open((dir + "/manifest.json").c_str(), FILE_WRITE);
    if (!f)
      return error("storage error", 500);
    size_t written =
        f.write(reinterpret_cast<const uint8_t *>(raw.data()), raw.size());
    f.flush();
    f.close();
    if (written != raw.size())
      return error("manifest write failed", 500);
    staging = rev;
    incoming = std::move(parsed);
    result["existing"] = false;
    reply(result);
  }
  void chunk() {
    if (!auth() || busy())
      return;
    if (staging.empty())
      return error("begin first", 409);
    String encoded = web.arg("path"), offsetText = web.arg("offset");
    std::string path(encoded.c_str(), encoded.length()), bytes;
    DynamicJsonDocument d(8192);
    if (!assetPath(path) || !json(d) || !conteuse::nonempty(d["data"]) ||
        !decode64(d["data"].as<const char *>(), bytes) || offsetText.isEmpty())
      return error("invalid encoded chunk");
    uint32_t offset = 0;
    for (unsigned i = 0; i < offsetText.length(); ++i) {
      char c = offsetText[i];
      if (c < '0' || c > '9' || offset > MaxAsset / 10)
        return error("invalid offset");
      offset = offset * 10 + unsigned(c - '0');
    }
    if (offset > MaxAsset)
      return error("invalid offset");
    const conteuse::Asset *asset = nullptr;
    for (const auto &a : incoming.assets)
      if (a.path == path)
        asset = &a;
    if (!asset || uint64_t(offset) + bytes.size() > asset->bytes)
      return error("undeclared asset/range");
    std::string dest = "/library/incoming/" + staging + "/" + path;
    if (!mkdirs(dest))
      return error("storage error", 500);
    File f = SD.open(dest.c_str(), FILE_APPEND);
    if (!f)
      return error("storage error", 500);
    if (f.size() != offset) {
      f.close();
      return error("offset conflict; restart transfer", 409);
    }
    size_t count =
        f.write(reinterpret_cast<const uint8_t *>(bytes.data()), bytes.size());
    f.flush();
    f.close();
    if (count != bytes.size())
      return error("short write", 500);
    StaticJsonDocument<128> result;
    result["next"] = offset + count;
    reply(result);
  }
  void startJob(bool commit) {
    if (!auth() || busy())
      return;
    DynamicJsonDocument d(512);
    if (!json(d) || !conteuse::nonempty(d["revision"]))
      return error("invalid job");
    std::string rev = d["revision"].as<const char *>();
    if (commit && (staging.empty() || staging != rev))
      return error("invalid commit");
    std::string id;
    if (!commit) {
      if (!conteuse::nonempty(d["uid"]))
        return error("invalid ID");
      id = d["uid"].as<const char *>();
      if (!uidValid(id))
        return error("invalid ID");
    }
    if (!verifier.begin(rev,
                        commit ? "/library/incoming/" : "/library/versions/"))
      return error("invalid stored manifest", 409);
    jobRevision = rev;
    jobUid = id;
    jobKind = commit ? "commit" : "assign";
    jobState = "pending";
    jobReply();
  }
  void advance() {
    if (jobState != "pending")
      return;
    verifier.step();
    if (verifier.pending)
      return;
    if (!verifier.valid) {
      jobState = "error";
      return;
    }
    bool ok = false;
    if (jobKind == "assign")
      ok = assign(jobUid, jobRevision);
    else {
      std::string dest = "/library/versions/" + jobRevision;
      if (!SD.exists(dest.c_str()) && mkdirs("/library/versions/placeholder"))
        ok = SD.rename(("/library/incoming/" + jobRevision).c_str(),
                       dest.c_str());
      if (ok) {
        staging.clear();
        incoming = conteuse::Content{};
      }
    }
    jobState = ok ? "done" : "error";
  }

public:
  bool active() const { return running; }
  void card(const std::string &id) {
    if (mutex)
      xSemaphoreTake(mutex, portMAX_DELAY);
    current = id;
    if (mutex)
      xSemaphoreGive(mutex);
  }
  bool start() {
    if (running)
      return true;
    if (SD.cardType() == CARD_NONE || !removeTree("/library/incoming"))
      return false;
    staging.clear();
    if (!mutex)
      mutex = xSemaphoreCreateMutex();
    if (!mutex)
      return false;
    // A bootstrap secured AP enables RF entropy before final credentials are
    // drawn.
    std::string bootstrap = randomHex(8);
    if (bootstrap.size() != 16)
      return false;
    WiFi.mode(WIFI_AP);
    if (!WiFi.softAPConfig(IPAddress(192, 168, 4, 1), IPAddress(192, 168, 4, 1),
                           IPAddress(255, 255, 255, 0))) {
      WiFi.mode(WIFI_OFF);
      return false;
    }
    if (!WiFi.softAP("Galia-initializing", bootstrap.c_str(), 1, false, 2)) {
      WiFi.mode(WIFI_OFF);
      return false;
    }
    token = randomHex(32);
    std::string password = randomHex(8), suffix = randomHex(3),
                ssid = "Galia-" + suffix;
    if (token.size() != 64 || password.size() != 16 || suffix.size() != 6 ||
        !WiFi.softAP(ssid.c_str(), password.c_str(), 1, false, 2)) {
      WiFi.softAPdisconnect(true);
      WiFi.mode(WIFI_OFF);
      token.clear();
      return false;
    }
    esp_wifi_deauth_sta(0); // Drop any station from the bootstrap credentials.
    started = lastRequest = millis();
    jobState = "idle";
    web.on("/api/status", HTTP_GET, [this]() {
      if (!auth())
        return;
      StaticJsonDocument<512> d;
      d["protocol"] = 1;
      d["current_card"] = current;
      if (!current.empty())
        d["assigned_revision"] = mapping(current).revision;
      d["remaining_seconds"] = (7200000 - uint32_t(millis() - started)) / 1000;
      reply(d);
    });
    web.on("/api/job", HTTP_GET, [this]() {
      if (auth())
        jobReply();
    });
    web.on("/api/begin", HTTP_POST, [this]() { beginTransfer(); });
    web.on("/api/chunk", HTTP_POST, [this]() { chunk(); });
    web.on("/api/commit", HTTP_POST, [this]() { startJob(true); });
    web.on("/api/assign", HTTP_POST, [this]() { startJob(false); });
    if (!web.begin(mutex)) {
      WiFi.softAPdisconnect(true);
      WiFi.mode(WIFI_OFF);
      token.clear();
      return false;
    }
    running = true;
    Serial.printf("PARENT SETUP (private; do not share): SSID=%s PASSWORD=%s "
                  "TOKEN=%s ADDRESS=192.168.4.1\n",
                  ssid.c_str(), password.c_str(), token.c_str());
    return true;
  }
  void stop() {
    if (!running)
      return;
    web.stop();
    verifier.cancel();
    WiFi.softAPdisconnect(true);
    WiFi.mode(WIFI_OFF);
    running = false;
    token.clear();
    current.clear();
    incoming = conteuse::Content{};
  }
  void tick() {
    if (!running)
      return;
    xSemaphoreTake(mutex, portMAX_DELAY);
    bool expired = uint32_t(millis() - started) >= 7200000 ||
                   uint32_t(millis() - lastRequest) >= 180000;
    if (!expired)
      advance();
    xSemaphoreGive(mutex);
    if (expired)
      stop();
  }
};
} // namespace admin
