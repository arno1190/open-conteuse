"""No live network: verify the boundary around redirects, TLS and limits."""
import unittest
from unittest.mock import patch
from conteuse.feeds import fetch, parse_rss


class Response:
    def __init__(self,status=200,body=b'ok',headers=None):
        self.status=status;self.body=body;self.headers=headers or {}
    def getheader(self,key,default=None):return self.headers.get(key,default)
    def read1(self,count):
        value=self.body[:count];self.body=self.body[count:];return value


class Connection:
    def __init__(self,response):self.response=response;self.sock=None
    def request(self,*args,**kwargs):pass
    def getresponse(self):return self.response
    def close(self):pass


class FetchTests(unittest.TestCase):
    def run_fetch(self,responses,url='https://example.org/audio',**kwargs):
        with patch('conteuse.feeds.public_addresses',return_value=['93.184.216.34']) as resolve, \
             patch('conteuse.feeds.socket.create_connection') as socket, \
             patch('conteuse.feeds.ssl.create_default_context') as context:
            # The fake connection exposes the TLS factory context for SNI checks.
            class TLSConnection(Connection):
                def __init__(self,response):super().__init__(response);self._context=context.return_value
            with patch('conteuse.feeds.http.client.HTTPSConnection',side_effect=[TLSConnection(r) for r in responses]):
                result=fetch(url,**kwargs)
            self.assertEqual(context.return_value.wrap_socket.call_args.kwargs['server_hostname'],'example.org')
            self.assertEqual(socket.call_args.args[0],('93.184.216.34',443))
            return result,resolve.call_count

    def test_checked_address_and_relative_redirect(self):
        result,count=self.run_fetch([Response(302,headers={'Location':'/new'}),Response(body=b'abc',headers={'Content-Length':'3'})])
        self.assertEqual(result,b'abc');self.assertEqual(count,2)

    def test_unsafe_redirects_and_urls(self):
        for url in ('http://example.org','https://user:secret@example.org','https://example.org:444','https://example.org/#fragment'):
            with self.assertRaises(ValueError):self.run_fetch([Response()],url)
        with self.assertRaises(ValueError):self.run_fetch([Response(302,headers={'Location':'http://localhost/internal'})])
    def test_oversize_truncated_compressed_and_status(self):
        for response in (Response(body=b'12345'),Response(headers={'Content-Length':'99'}),
                         Response(headers={'Content-Length':'3'}),Response(headers={'Content-Encoding':'gzip'}),Response(404)):
            with self.subTest(response=response.headers):
                with self.assertRaises(ValueError):self.run_fetch([response],limit=4)

    def test_utf16_xml_cannot_hide_entities(self):
        with self.assertRaises((ValueError,UnicodeError)):
            parse_rss('<!DOCTYPE rss [<!ENTITY x "hello">]><rss/>'.encode('utf-16'))
