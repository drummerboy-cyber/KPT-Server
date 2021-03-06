# Copyright (c) 2012, AverageSecurityGuy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   Neither the name of AverageSecurityGuy nor the names of its contributors may
#   be used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.

import time
import base64
import random
import urllib
import urlparse
import hmac
import hashlib


class SimpleOAuth():
    '''Creates an OAuth authorization header.'''
    def __init__(self, ck, cs, at, ats, url, stamp=None, nonce=None,
                 body=None, method='GET'):
        self.consumer_key = ck
        self.consumer_secret = cs
        self.access_token = at
        self.access_token_secret = ats
        self.__base_url = self.__get_base_url(url)
        self.__body = self.__get_body_params(body)
        self.__query = self.__get_query_params(url)
        self.__method = method.upper()

        if stamp == None:
            self.__time = int(time.time())
        else:
            self.__time = stamp

        if nonce is None:
            self.__nonce = self.__get_nonce()
        else:
            self.__nonce = nonce

    def calculate_oauth(self):
        '''Return the authorization header needed.'''
        return self.__generate_auth_string()

    def __enc(self, string):
        encoded_str = urllib.quote(string, safe='')
        return encoded_str.replace('+', '%20').replace('%7E', '~')

    def __get_nonce(self, length=32):
        n = ''
        for i in range(length):
            n += random.choice('0123456789ABCDEF')

        return n

    def __get_base_url(self, url):
        url = url.split('?')

        return url[0]

    def __get_query_params(self, url):
        q = {}
        query = urlparse.urlparse(url).query

        if query != '':
            for param in query.split('&'):
                key, val = param.split('=')
                q[key] = val

        return q

    def __get_body_params(self, body):
        b = {}

        if body is not None:
            body = body.replace('+', ' ')
            body = urllib.unquote(body)
            for p in body.split('&'):
                key, val = p.split('=')
                b[key] = val

        return b

    def __calculate_signature(self):
        base = self.__generate_base_string()
        key = self.__generate_signing_key()
        signature = hmac.new(key, base, hashlib.sha1)

        return base64.b64encode(signature.digest())

    def __generate_base_string(self):
        base = self.__method + '&'

        base += self.__enc(self.__base_url) + '&'
        base += self.__enc(self.__generate_parameter_string())

        return base

    def __generate_parameter_string(self):
        p = {}
        p['oauth_consumer_key'] = self.__enc(self.consumer_key)
        p['oauth_nonce'] = self.__enc(self.__nonce)
        p['oauth_signature_method'] = 'HMAC-SHA1'
        p['oauth_timestamp'] = self.__time
        p['oauth_token'] = self.__enc(self.access_token)
        p['oauth_version'] = '1.0'

        for k, v in self.__query.iteritems():
            p[self.__enc(k)] = self.__enc(v)

        for k, v in self.__body.iteritems():
            p[self.__enc(k)] = self.__enc(v)

        pstr = '&'.join(['{0}={1}'.format(k, p[k]) for k in sorted(p)])

        return pstr

    def __generate_signing_key(self):
        key = self.__enc(self.consumer_secret)
        key += '&'
        key += self.__enc(self.access_token_secret)

        return key

    def __generate_auth_string(self):
        a = 'OAuth '
        a += 'oauth_consumer_key="{0}", '.format(self.__enc(self.consumer_key))
        a += 'oauth_nonce="{0}", '.format(self.__enc(self.__nonce))
        a += 'oauth_signature="{0}", '.format(self.__enc(self.__calculate_signature()))
        a += 'oauth_signature_method="HMAC-SHA1", '
        a += 'oauth_timestamp="{0}", '.format(self.__time)
        a += 'oauth_token="{0}", '.format(self.__enc(self.access_token))
        a += 'oauth_version="1.0"'

        return a
