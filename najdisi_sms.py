#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import logging

import requests
from bs4 import BeautifulSoup

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
        recipent = who.replace(' ', '')[3:]
        # 031 123 456 =>  031
        base_code = who[:3]

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

        base_code, recipient = self.normalize_receiver(receiver)

        log.info('Omrezna koda: %s', base_code)
        log.info('Prejemnik: %s', recipient)
        log.info('Sporocilo: %s',  msg)
        log.info('Posiljam sms ...')

        s = requests.Session()
        s.headers.update({'User-Agent': self.useragent})

        response = s.get(
            'http://www.najdi.si/najdi.layoutnajdi.loginlink:login?t:ac=sms'
        )

        soup = BeautifulSoup(response.text)
        formdata_els = soup.findAll(attrs={'name': 't:formdata'})
        formdata_value = formdata_els[0].attrs['value']

        data = {
            't:formdata': formdata_value,
            'jsecLogin': 'brodul',
            'jsecPassword': 'HbI2tsiTPb6z'
        }
        response = s.post(
            'http://www.najdi.si/prijava.jsecloginform',
            data
        )

        soup = BeautifulSoup(response.text)
        formdata_els = soup.findAll(attrs={'name': 't:formdata'})
        formdata_vals = [formdata_el.attrs['value'] for formdata_el in formdata_els]
        hidden_els = soup.findAll(attrs={'name': 'hidden'})
        hidden_value = hidden_els[0].attrs['value']

        data = {
            't:ac': 'sms',
            't:formdata': formdata_vals,
            'areaCodeRecipient': base_code,
            'phoneNumberRecipient': recipient,
            'selectLru': '',
            'hidden': hidden_value,
            'name': '',
            'areaCodeLru': '031',
            'phoneNumberLru': '722959',
            'text': msg,
            't:submit': '["send","send"]',
            't:zoneid': 'smsZone'
        }
        response = s.post(
            "http://www.najdi.si/najdi.shortcutplaceholder.freesmsshortcut.smsform",
            data
        )
        soup = BeautifulSoup(response.text)

if __name__ == '__main__':
    main()
