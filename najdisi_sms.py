#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import urllib
import urllib2
import httplib
import cookielib
from optparse import OptionParser

import mechanize


def main():
    parser = OptionParser(usage="%prog [options] who msg")
    parser.add_option("-u", "--username", dest="username", help=u"Uporabniško ime")
    parser.add_option("-p", "--password", dest="password", help=u"Geslo")
    parser.add_option("-A", "--useragent", dest="useragent", help=u"HTTP User Agent",
        default="Mozilla/5.0 (Windows; U; Windows NT 6.1; es-ES; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3")
    (options, args) = parser.parse_args()
    who = args.pop(0)
    msg = ' '.join(args)

    # don't change
    temp_recipent=who.strip().replace(' ', '')[3:]
    recipent=temp_recipent[:3] + ' ' + temp_recipent[3:]
    base_code=int(who[1:3])

    if len(msg) > 160:
        raise Exception('predolgo sporocilo')

    print 'Omrezna koda: %s' % base_code
    print 'Prejemnik: %s' % recipent
    print 'Sporocilo: %s' % msg
    print '\nPosiljam sms ...'

    # handlers and headers
    jar = cookielib.CookieJar()
    handler = urllib2.HTTPCookieProcessor(jar)
    handler2 = urllib2.HTTPHandler()
    handler3 = urllib2.HTTPSHandler()
    handler4 = mechanize.HTTPRefererProcessor()
    opener = urllib2.build_opener(handler3, handler2, handler, handler4)
    opener.addheaders = [
        ("User-agent", options.useragent),
    ]
    urllib2.install_opener(opener)

    # authentication
    data = urllib.urlencode({
        'j_username': options.username,
        'j_password': options.password,
        '_spring_security_remember_me': 'on',
    })
    urllib2.urlopen("https://id.najdi.si/j_spring_security_check", data)

    # timestamp cookie
    chkcookie = str(time.time()).replace('.', '')
    while len(chkcookie) < 13:
        chkcookie += '0'

    data=urllib.urlencode({
        'sms_action': '4',
        'sms_so_ac_%s' % chkcookie: base_code,
        'sms_so_l_%s' % chkcookie: recipent,
        'myContacts': '',
        'sms_message_%s' % chkcookie: msg.strip(),
    })

    req = urllib2.Request("http://www.najdi.si/sms/smsController.jsp?" + data)
    cookie_tuple = jar._normalized_cookie_tuples([
        [('chkcookie', chkcookie),
        ('domain', 'www.najdi.si')],
    ])
    cookie = jar._cookie_from_cookie_tuple(cookie_tuple[0], req)
    jar.set_cookie(cookie)
    cookie_tuple = jar._normalized_cookie_tuples([
        [('lganchor', 'freesms'),
        ('domain', 'www.najdi.si')],
    ])
    cookie = jar._cookie_from_cookie_tuple(cookie_tuple[0], req)
    jar.set_cookie(cookie)

    # second step authentication
    urllib2.urlopen("http://www.najdi.si/auth/login.jsp?sms=1&target_url=http%3A%2F%2Fwww.najdi.si%2Findex.jsp")

    # validate authentication
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    urllib2.urlopen("http://www.najdi.si/auth/isPrincipalAlive.jsp")

    # send sms
    r = urllib2.urlopen(req)
    d = json.loads(r.read())
    if d['dialog'] == 3:
        print 'Uspelo. Preostalih smsov danes: %d' % d['msg_left']
    else:
        print 'Napaka: %r' % d

if __name__ == '__main__':
    main()
