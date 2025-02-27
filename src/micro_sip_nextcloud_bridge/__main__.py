import tempfile
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
from requests.auth import HTTPBasicAuth
from vobject.base import readOne
from wiederverwendbar.logger import LoggerSingleton
from wiederverwendbar.uvicorn import UvicornServer

from micro_sip_nextcloud_bridge import __name__ as __module_name__, __title__, __description__, __version__, __author__, __author_email__
from micro_sip_nextcloud_bridge.settings import Settings

FILES_PATH = Path(tempfile.gettempdir()) / __module_name__

settings = Settings()

logger = LoggerSingleton(name=__module_name__, settings=settings, init=True)

app = FastAPI(
    title=__title__,
    description=__description__,
    version=__version__,
    contact={
        "name": __author__,
        "email": __author_email__,
    }
)


def nice_number(phone_number: str, country_code: str) -> str:
    """
    Strips space, -, ( and ) from the given string, replaces counrty cody with 0 and returns the string
    """

    nice_phone_number = phone_number
    nice_phone_number = nice_phone_number.replace(" ", "")
    nice_phone_number = nice_phone_number.replace("-", "")
    nice_phone_number = nice_phone_number.replace("(", "")
    nice_phone_number = nice_phone_number.replace(")", "")
    if nice_phone_number.startswith("0"):
        nice_phone_number = country_code + nice_phone_number[1:]
    return nice_phone_number


last_contacts_update: float = 0


@app.get("/", response_class=FileResponse, summary="Returns contacts as xml")
def contacts() -> FileResponse:
    global last_contacts_update

    logger.info("Getting contacts ...")

    FILES_PATH.mkdir(parents=True, exist_ok=True)

    xml_file_path = FILES_PATH / "contacts.xml"

    if settings.use_cached_contacts:
        cache_timeout = last_contacts_update + settings.contacts_update_interval - time.time()
        if cache_timeout < 0:
            cache_timeout = 0
    else:
        cache_timeout = 0

    if cache_timeout == 0:
        if xml_file_path.is_file():
            xml_file_path.unlink()

    if not xml_file_path.is_file():
        logger.info("Getting Nextcloud Address books ...")

        xml_file = open(xml_file_path, "w", encoding="utf8")
        xml_file.write(u"\ufeff")
        xml_file.write("<?xml version=\"1.0\"?>\n")
        xml_file.write("<contacts>\n")

        for address_book in settings.address_books:
            logger.info(f"Getting address book \"{address_book.url}\" ...")
            try:
                # retrieves CardDAV data
                response = requests.get(f"{address_book.url}/?export", auth=HTTPBasicAuth(address_book.user, address_book.password))
                address_book_data = str(response.content.decode("utf-8"))

                # Turns the retrieved data into VCard objects
                for i in str(address_book_data).replace("\\r\\n", "\n").split("END:VCARD")[:-1]:
                    card = readOne(i + "END:VCARD\n")
                    try:
                        _o = card.org.value
                    except:
                        card.add("org").value = [""]
                    try:
                        if card.org.value[0] != "":
                            _org = "{}, ".format(card.org.value[0])
                        else:
                            _org = ""
                        for tel in getattr(card, "tel_list", []):
                            if tel.type_param == "HOME":
                                xml_file.write("<contact number=\"{}\"  name=\"{} ({}Home)\" presence=\"0\" directory=\"0\" ></contact>\n".format(
                                    nice_number(phone_number=tel.value, country_code=address_book.country_code),
                                    card.fn.value,
                                    _org))
                            elif tel.type_param == "WORK":
                                xml_file.write("<contact number=\"{}\" name=\"{} ({}Work)\" presence=\"0\" directory=\"0\" ></contact>\n".format(
                                    nice_number(phone_number=tel.value, country_code=address_book.country_code),
                                    card.fn.value,
                                    _org))
                            elif tel.type_param == "CELL":
                                xml_file.write(
                                    "<contact number=\"{}\"  name=\"{} ({}Mobile)\" presence=\"0\" directory=\"0\" ></contact>\n".format(
                                        nice_number(phone_number=tel.value, country_code=address_book.country_code),
                                        card.fn.value,
                                        _org))
                            else:
                                xml_file.write(
                                    "<contact number=\"{}\"  name=\"{} ({}Voice)\" presence=\"0\" directory=\"0\" ></contact>\n".format(
                                        nice_number(phone_number=tel.value, country_code=address_book.country_code),
                                        card.fn.value,
                                        _org))
                    except Exception as e:
                        logger.error(f"Error while processing contact \"{card.fn.value}\" from address book \"{address_book.url}\":\n{e}")
            except Exception as e:
                logger.error(f"Error while getting address book \"{address_book.url}\":\n{e}")
        logger.info("Getting Nextcloud Address books ... done")

        xml_file.write("</contacts>\n")
        xml_file.close()
        last_contacts_update = time.time()
    else:
        logger.info("Using cached contacts")

    return FileResponse(
        path=xml_file_path,
        media_type="application/xml",

    )


def main():
    logger.info(f"{__title__}")
    logger.info(f"Version: {__version__}")
    logger.info(f"Author: {__author__} ({__author_email__})")

    UvicornServer(app=app, settings=settings)


if __name__ == "__main__":
    main()
