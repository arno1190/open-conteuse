"""Bounded RSS ingestion. No Apple/Spotify export; no automatic audio approval."""
import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urljoin, urlsplit
import xml.etree.ElementTree as ET

LIMIT = 32 * 1024 * 1024


def public_addresses(host):
    addresses = sorted({item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)})
    if not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses):
        raise ValueError("destination must resolve only to public addresses")
    return addresses


def fetch(url, limit=LIMIT, redirects=3):
    """HTTPS-only, pin checked DNS address per connection, recheck every redirect.

    No proxy/environment credentials, decompression, cookies or authorization.
    Check a 30-second transfer deadline between reads; socket timeout is five
    seconds. DNS/HTTP header parsing are not hard real-time bounded.
    """
    import time
    deadline = time.monotonic() + 30
    if not 0 < limit <= LIMIT:
        raise ValueError("invalid download bound")
    for hop in range(redirects + 1):
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
                or parsed.port not in (None, 443) or parsed.fragment):
            raise ValueError("only public HTTPS URLs on port 443 are accepted")
        address = public_addresses(parsed.hostname)[0]
        connection = http.client.HTTPSConnection(parsed.hostname, timeout=5, context=ssl.create_default_context())
        # Pin IP while retaining TLS certificate/SNI checks for the original host.
        raw = socket.create_connection((address, 443), timeout=5)
        try:
            connection.sock = connection._context.wrap_socket(raw, server_hostname=parsed.hostname)
            connection.request("GET", (parsed.path or "/") + ("?" + parsed.query if parsed.query else ""),
                               headers={"Accept-Encoding": "identity", "User-Agent": "OpenConteuse/0.1"})
            response = connection.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader("Location")
                if not location or hop == redirects:
                    raise ValueError("redirect limit or missing location")
                url = urljoin(url, location)
                continue
            if response.status != 200 or response.getheader("Content-Encoding", "identity") != "identity":
                raise ValueError("unsupported HTTP response")
            length = response.getheader("Content-Length")
            if length is not None and (not length.isdecimal() or int(length) > limit):
                raise ValueError("oversized response")
            chunks, count = [], 0
            while True:
                if time.monotonic() > deadline:
                    raise ValueError("transfer deadline exceeded")
                chunk = response.read1(min(65536, limit + 1 - count))
                if not chunk:
                    break
                chunks.append(chunk)
                count += len(chunk)
                if count > limit:
                    raise ValueError("download quota exceeded")
            if length is not None and count != int(length):
                raise ValueError("truncated response")
            return b"".join(chunks)
        finally:
            connection.close()
            raw.close()
    raise ValueError("redirect limit")


def parse_rss(data):
    if len(data) > 1024 * 1024 or b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("oversized RSS or forbidden XML declaration")
    # UTF-8 only prevents UTF-16/32 encodings from hiding DTD declarations.
    text = data.decode("utf-8-sig")
    if "<!DOCTYPE" in text.upper() or "<!ENTITY" in text.upper() or "\x00" in text:
        raise ValueError("forbidden XML declaration or encoding")
    root = ET.fromstring(text)
    if root.tag != "rss":
        raise ValueError("RSS 2.0 expected")
    episodes, seen = [], set()
    for item in root.findall("./channel/item"):
        guid = item.findtext("guid")
        enclosure = item.find("enclosure")
        if not guid or enclosure is None or guid in seen:
            raise ValueError("missing/duplicate episode GUID or enclosure")
        url, mime = enclosure.get("url", ""), enclosure.get("type", "")
        if mime not in ("audio/mpeg", "audio/aac", "audio/mp4") or urlsplit(url).scheme != "https":
            raise ValueError("unsupported audio enclosure")
        seen.add(guid)
        episodes.append({"guid": guid, "title": item.findtext("title", "Untitled"), "url": url, "mime": mime})
    return episodes


def station_capability(url, mime):
    if urlsplit(url).scheme not in ("http", "https") or not urlsplit(url).hostname:
        raise ValueError("invalid station URL")
    return "direct" if mime in ("audio/mpeg", "audio/aac") else "unsupported"
