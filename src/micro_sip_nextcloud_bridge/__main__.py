import configparser
import os
import re
import codecs
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from vobject import readOne
from vobject.vcard import VCard3_0

from micro_sip_nextcloud_bridge import __title__, __version__, __author__, __author_email__
from micro_sip_nextcloud_bridge.logger import logger
from micro_sip_nextcloud_bridge.settings import settings

settings()

MICRO_SIP_CONFIG_PATH = Path(os.environ["APPDATA"]) / "MicroSIP"


def set_micro_sip_config():
    logger().info("Setting MicroSIP config ...")

    MICRO_SIP_CONFIG_PATH.mkdir(parents=True, exist_ok=True)

    # read src config
    with codecs.open(settings().micro_sip_src_config_path, "r", encoding="utf-16le") as f:
        micro_sip_src_config_content = f.read()

    # remove first symbol in not '['
    if micro_sip_src_config_content[0] != "[":
        micro_sip_src_config_content = micro_sip_src_config_content[1:]

    # replace '%USERNAME% with environment variable
    micro_sip_src_config_content = micro_sip_src_config_content.replace('%USERNAME%', os.environ["USERNAME"])

    # write config
    with codecs.open(MICRO_SIP_CONFIG_PATH / settings().micro_sip_src_config_path.name, "w", encoding="utf-16") as f:
        f.write(micro_sip_src_config_content)

    # append accounts to config file
    for micro_sip_src_account_file in settings().micro_sip_src_accounts_path:
        # read account file
        with codecs.open(micro_sip_src_account_file, "r", encoding="utf-16") as f:
            micro_sip_src_account_file_content = f.read()

        # remove first symbol in not '['
        if micro_sip_src_account_file_content[0] != "[":
            micro_sip_src_account_file_content = micro_sip_src_account_file_content[1:]

        # write to config
        with codecs.open(MICRO_SIP_CONFIG_PATH / settings().micro_sip_src_config_path.name, "a", encoding="utf-16") as f:
            f.write(micro_sip_src_account_file_content)

    logger().info("Setting MicroSIP config ... done")


def get_nextcloud_address_books() -> list[VCard3_0]:
    logger().info("Getting Nextcloud Address books ...")

    cards = []
    for nextcloud_address_book in settings().nextcloud_address_books:
        logger().info(f"Getting address book '{nextcloud_address_book.url}' ...")
        try:
            # retrieves CardDAV data
            response = requests.get(f"{nextcloud_address_book.url}/?export", auth=HTTPBasicAuth(nextcloud_address_book.user, nextcloud_address_book.password))
            nextcloud_address_book_data = str(response.content.decode("utf-8"))

            # Turns the retrieved data into VCard objects
            _l = str(nextcloud_address_book_data).replace('\\r\\n', '\n').split('END:VCARD')
            _l.pop(-1)
            _cards = []
            for i in _l:
                v = readOne(i + 'END:VCARD\n')
                try:
                    _o = v.org.value
                except:
                    v.add('org').value = ['']
                _cards.append(v)
            cards.extend(_cards)
            logger().info(f"Got {len(_cards)} contacts from address book '{nextcloud_address_book.url}'.")
        except Exception as e:
            logger().error(f"Error while getting address book '{nextcloud_address_book.url}':\n{e}")
    logger().info("Getting Nextcloud Address books ... done")
    return cards


def get_country_code() -> str:
    """
    Tries to find country code info in MicroSIP config file and returns it.
    """

    micro_sip_config = configparser.ConfigParser()
    micro_sip_config.read_file(codecs.open(MICRO_SIP_CONFIG_PATH / settings().micro_sip_src_config_path.name, "r", "utf16"))

    p = re.compile('(\+[0-9]{1,3})')
    for section in micro_sip_config.sections():
        if micro_sip_config.has_option(section, "dialPlan"):
            m = p.search(micro_sip_config.get(section, "dialPlan"))
            if m:
                return m.group(1)
    return "+49"


def nice_number(phone_number) -> str:
    """
    Strips space, -, ( and ) from the given string, replaces counrty cody with 0 and returns the string
    """

    nice_phone_number = phone_number.replace(get_country_code(), "0").replace(" ", "").replace("-", "").replace("(", "").replace(")", "").strip()
    return nice_phone_number


def export_to_xml(cards):
    """
    Exports the given list into an XML file
    """

    logger().info("Writing Contacts.xml ...")

    f = open(MICRO_SIP_CONFIG_PATH / "Contacts.xml", "w", encoding="utf8")
    f.write(u'\ufeff')
    f.write('<?xml version="1.0"?>\n')
    f.write('<contacts>\n')
    for card in cards:
        try:
            if card.org.value[0] != '':
                _org = '{}, '.format(card.org.value[0])
            else:
                _org = ''
            for tel in card.tel_list:
                if tel.type_param == 'HOME':
                    f.write('<contact number="{}"  name="{} ({}Home)" presence="0" directory="0" ></contact>\n'.format(nice_number(tel.value), card.fn.value, _org))
                elif tel.type_param == 'WORK':
                    f.write('<contact number="{}" name="{} ({}Work)" presence="0" directory="0" ></contact>\n'.format(nice_number(tel.value), card.fn.value, _org))
                elif tel.type_param == 'CELL':
                    f.write('<contact number="{}"  name="{} ({}Mobile)" presence="0" directory="0" ></contact>\n'.format(nice_number(tel.value), card.fn.value, _org))
                else:
                    f.write('<contact number="{}"  name="{} ({}Voice)" presence="0" directory="0" ></contact>\n'.format(nice_number(tel.value), card.fn.value, _org))
        except:
            continue
    f.write('</contacts>\n')
    f.close()

    logger().info("Writing Contacts.xml ... done")


def main():
    logger().info(f"{__title__}")
    logger().info(f"Version: {__version__}")
    logger().info(f"Author: {__author__} ({__author_email__})")

    set_micro_sip_config()

    cards = get_nextcloud_address_books()
    export_to_xml(cards)


if __name__ == '__main__':
    main()
