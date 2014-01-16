#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import urllib
import urllib2
import cookielib
from optparse import OptionParser
import logging

import mechanize

logging.basicConfig()
log = logging.getLogger("najdisi_sms")
log.setLevel(logging.INFO)


def main():
    parser = OptionParser(usage="%prog [options] who msg")
    parser.add_option(
        "-u",
        "--username",
        dest="username",
        help=u"Uporabniško ime"
    )
    parser.add_option(
        "-p",
        "--password",
        dest="password",
        help=u"Geslo"
    )
    parser.add_option(
        "-A",
        "--useragent",
        dest="useragent",
        help=u"HTTP User Agent",
        default="Mozilla/5.0 (Windows; U; Windows NT 6.1; es-ES; rv:1.9.2.3)"
        + "Gecko/20100401 Firefox/3.6.3"
    )
    (options, args) = parser.parse_args()
    who = args.pop(0)
    msg = ' '.join(args)

    sender = SMSSender(options.username, options.password, options.useragent)
    sender.sent(who, msg)


class SMSSender(object):
    """Docstring for SMSSender. """

    def __init__(self, username, password, useragent=""):
        """@todo: to be defined1. """
        self.username = username
        self.password = password
        da = "Mozilla/5.0 (Windows; U; Windows NT 6.1; es-ES; rv:1.9.2.3)" \
            + "Gecko/20100401 Firefox/3.6.3"
        self.useragent = useragent or da

    def normalize_receiver(self, receiver_num):
        """
        Split telephone number into area code and local number.


        :receiver_num: Telephone number string.
        :returns: Tuple with area code and local number.

        """
        # 031 123 456
        who = receiver_num.strip()

        # don't change
        # 031 123 456 => 123456
        temp_recipent = who.replace(' ', '')[3:]
        # 123456 => 123 456
        recipent = temp_recipent[:3] + ' ' + temp_recipent[3:]
        # 031 123 456 =>  31
        base_code = int(who[1:3])

        return base_code, recipent

    def check_msg_leng(self, msg):
        """
        Checks the message length raises an exception if more than 160 chars.

        :msg: Message
        :returns: Returns non modified msg

        """
        if len(msg) > 160:
            raise Exception('predolgo sporocilo')

        return msg

    def sent(self, receiver, msg):
        """Sent the message.

        :receiver: Reciever number (only Slovenian supported)
        :msg: SMS body message
        :returns: True if sending succeeded, else False.

        """

        msg = self.check_msg_leng(msg)

        base_code, recipent = self.normalize_receiver(receiver)

        log.info('Omrezna koda: %s', base_code)
        log.info('Prejemnik: %s', recipent)
        log.info('Sporocilo: %s',  msg)
        log.info('Posiljam sms ...')

        # handlers and headers
        jar = cookielib.CookieJar()
        handler = urllib2.HTTPCookieProcessor(jar)
        handler2 = urllib2.HTTPHandler()
        handler3 = urllib2.HTTPSHandler()
        handler4 = mechanize.HTTPRefererProcessor()
        opener = urllib2.build_opener(handler3, handler2, handler, handler4)
        opener.addheaders = [
            ("User-agent", self.useragent),
        ]
        urllib2.install_opener(opener)

        # authentication
        data = urllib.urlencode({
            'j_username': self.username,
            'j_password': self.password,
            '_spring_security_remember_me': 'on',
        })
        urllib2.urlopen("https://id.najdi.si/j_spring_security_check", data)

        # timestamp cookie
        chkcookie = str(time.time()).replace('.', '')
        while len(chkcookie) < 13:
            chkcookie += '0'

        data = urllib.urlencode({
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
        urllib2.urlopen(
            "http://www.najdi.si/auth/login.jsp" +
            "?sms=1&target_url=http%3A%2F%2Fwww.najdi.si%2Findex.jsp"
        )

        # validate authentication
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        urllib2.urlopen("http://www.najdi.si/auth/isPrincipalAlive.jsp")

        # send sms
        r = urllib2.urlopen(req)
        d = json.loads(r.read())
        if d['dialog'] == 3:
            log.info('Uspelo. Preostalih smsov danes: %d',  d['msg_left'])
            return True
        else:
            log.info('Napaka: %r', d)
        return False


if __name__ == '__main__':
    main()
