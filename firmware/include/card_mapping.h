// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "admin_protocol.h"
#include "content.h"
namespace admin {
struct Mapping {
  std::string revision;
  uint32_t generation = 0;
  int slot = -1;
};
inline std::string mappingJson(const std::string &revision, uint32_t generation,
                               const std::string &digest) {
  return "{\"generation\":" + std::to_string(generation) + ",\"revision\":\"" +
         revision + "\",\"sha256\":\"" + digest + "\"}";
}
// Store is an injected filesystem seam. Hash is SHA256 on device.
template <class Hash>
Mapping decodeMapping(const std::string &raw, const std::string &id, int slot,
                      Hash hash) {
  Mapping out;
  if (raw.size() > 512 || !uidValid(id))
    return out;
  StaticJsonDocument<768> d;
  if (deserializeJson(d, raw) || !d.template is<JsonObject>() ||
      d.size() != 3 ||
      !conteuse::stringsValid(d.template as<JsonVariantConst>()) ||
      !d["generation"].template is<uint32_t>() ||
      !conteuse::nonempty(d["revision"]) || !conteuse::nonempty(d["sha256"]))
    return out;
  std::string revision = d["revision"].template as<const char *>();
  uint32_t gen = d["generation"].template as<uint32_t>();
  if (!gen || !conteuse::digestValid(revision) ||
      hash(id + ":" + revision + ":" + std::to_string(gen)) !=
          d["sha256"].template as<const char *>())
    return out;
  const auto expected = hash(id + ":" + revision + ":" + std::to_string(gen));
  if (raw != mappingJson(revision, gen, expected))
    return out;
  out.revision = revision;
  out.generation = gen;
  out.slot = slot;
  return out;
}
inline std::string mappingPath(const std::string &id, int slot) {
  return "/library/cards/" + id + "." + std::to_string(slot) + ".json";
}
template <class Store, class Hash>
Mapping readMapping(Store &store, const std::string &id, Hash hash) {
  Mapping best;
  if (!uidValid(id))
    return best;
  for (int slot = 0; slot < 2; ++slot) {
    auto candidate =
        decodeMapping(store.read(mappingPath(id, slot)), id, slot, hash);
    if (candidate.generation > best.generation)
      best = candidate;
  }
  return best;
}
template <class Store, class Hash>
bool writeMapping(Store &store, const std::string &id,
                  const std::string &revision, Hash hash) {
  if (!uidValid(id) || !conteuse::digestValid(revision))
    return false;
  auto before = readMapping(store, id, hash);
  if (before.generation == UINT32_MAX)
    return false;
  uint32_t generation = before.generation + 1;
  int slot = before.slot == 0 ? 1 : 0;
  auto path = mappingPath(id, slot), temp = path + ".tmp";
  const auto digest =
      hash(id + ":" + revision + ":" + std::to_string(generation));
  if (!conteuse::digestValid(digest))
    return false;
  const std::string raw = mappingJson(revision, generation, digest);
  if (!store.write(temp, raw))
    return false;
  auto verified = decodeMapping(store.read(temp), id, slot, hash);
  if (verified.generation != generation || verified.revision != revision)
    return false;
  if (!store.remove(path) || !store.rename(temp, path))
    return false;
  auto after = readMapping(store, id, hash);
  return after.generation == generation && after.revision == revision;
}
} // namespace admin
