#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO extensions? switch to M2Crypto?
import ssl
import sys
import json
from urllib.parse import urlparse
from OpenSSL import crypto
from OpenSSL._util import lib as cryptolib

def decode_x509name(n):
    return [ {'key': x.decode('utf8'), 'value': y.decode('utf8')} for (x,y) in n.get_components() ]

def pem_publickey(pkey):
    """ Format a public key as a PEM """
    bio = crypto._new_mem_buf()
    cryptolib.PEM_write_bio_PUBKEY(bio, pkey._pkey)
    return crypto._bio_to_string(bio)

def decode_x509cert(cert):
    return {
        'digest': {
            'md5':      cert.digest('md5').decode('utf8').replace(':',''),
            'sha1':     cert.digest('sha1').decode('utf8').replace(':',''),
            'sha256':   cert.digest('sha256').decode('utf8').replace(':','')
        },
        'subject': decode_x509name(cert.get_subject()),
        'expired': cert.has_expired(),
        'not_before': cert.get_notBefore().decode('utf8'),
        'not_after': cert.get_notAfter().decode('utf8'),
        'issuer': decode_x509name(cert.get_issuer()),
        'pubkey': pem_publickey(cert.get_pubkey()).decode('utf8'),
        'serial_number': cert.get_serial_number(),
        'version': cert.get_version()
    }

def cert21(orig_uri):
    if '://' in orig_uri:
      uri = urlparse(orig_uri)
      host = uri.hostname
      port = uri.port
    elif ':' in orig_uri:
      (host,port) = orig_uri.split(':')
    else:
      host = orig_uri

    if host is None:
      raise ValueError("unexpected uri " + orig_uri + " (no host)")

    if port is None:
      port = 443

    # The selection of the protocol version is quite sensitive
    sslcert = ssl.get_server_certificate((host, port), ssl_version=ssl.PROTOCOL_TLSv1_2)
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, sslcert)
    return {'cert': decode_x509cert(cert)}


if __name__ == '__main__':
    print(json.dumps(cert21(sys.argv[1]), indent=4, sort_keys=True))
