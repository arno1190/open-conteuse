"""Write current physical-card mapping slots to a powered-off player's mounted SD."""
import hashlib
import hmac
import json
from pathlib import Path
from .device import check_device_pack
from .packages import HEX, atomic_json, revision
from .wifi import card_uid


def checksum(uid, digest, generation):
    return hashlib.sha256(f'{uid}:{digest}:{generation}'.encode('ascii')).hexdigest()


def read_slot(path, uid):
    try:
        if path.stat().st_size > 512: return None
        value = json.loads(path.read_bytes())
        if not isinstance(value, dict): return None
        digest, generation, sha = (value.get(k) for k in ('revision','generation','sha256'))
        if (not isinstance(digest,str) or not HEX.fullmatch(digest)
                or not isinstance(generation,int) or isinstance(generation,bool)
                or not 1 <= generation <= 0xffffffff or not isinstance(sha,str)
                or not hmac.compare_digest(sha,checksum(uid,digest,generation))):
            return None
        return value
    except (OSError,ValueError,TypeError):
        return None


def export_assignments(library, cards, approvals):
    library = Path(library)
    verified, exported, skipped = {}, [], {}
    physical = {}
    conflicts = set()
    for original,digest in cards.items():
        try: normalized = card_uid(original)
        except ValueError: continue
        if normalized in physical and physical[normalized] != digest: conflicts.add(normalized)
        physical[normalized] = digest
    for original, digest in cards.items():
        try: uid = card_uid(original)
        except ValueError:
            skipped[original] = 'not a physical DS2401 ROM ID'
            continue
        if uid in conflicts:
            skipped[original] = 'conflicting case aliases; reassign this physical card'
            continue
        if uid in exported: continue
        if not isinstance(digest,str) or not HEX.fullmatch(digest) or digest not in approvals:
            skipped[original] = 'revision is not approved'
            continue
        if digest not in verified:
            try: verified[digest] = revision(check_device_pack(library/'versions'/digest)) == digest
            except (OSError,ValueError): verified[digest] = False
        if not verified[digest]:
            skipped[original] = 'device-compatible revision is not present and verified on this SD'
            continue
        paths = [library/'cards'/f'{uid}.{slot}.json' for slot in (0,1)]
        slots = [(read_slot(path,uid),slot) for slot,path in enumerate(paths)]
        valid = [(value,slot) for value,slot in slots if value is not None]
        before, active = max(valid,key=lambda item:item[0]['generation']) if valid else ({'generation':0},-1)
        if before.get('revision') == digest:
            exported.append(uid)
            continue
        generation = before['generation'] + 1
        if generation > 0xffffffff: raise ValueError('card mapping generation exhausted')
        target = paths[1 if active == 0 else 0]
        value = {'revision':digest,'generation':generation,'sha256':checksum(uid,digest,generation)}
        # Replace only the inactive slot; the previous valid record remains untouched.
        atomic_json(target,value)
        if read_slot(target,uid) != value:
            raise ValueError('SD assignment not confirmed; inspect the card records before retrying')
        exported.append(uid)
    return {'exported_cards':exported,'skipped_cards':skipped}
