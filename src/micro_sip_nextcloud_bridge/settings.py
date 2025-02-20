import os
import sys
from pathlib import Path

from pydantic import Field, BaseModel, FilePath, DirectoryPath, ValidationError
from wiederverwendbar.singleton import Singleton
from wiederverwendbar.pydantic import ModelSingleton, FileConfig
from wiederverwendbar.logger import LoggerSettings

SETTINGS_FILE_NAME: str = "settings.json"
SETTINGS_LOOKUP_PATHS: list[Path] = [
    Path("."),
    Path("/usr/local/etc/nextcloud-micos-export"),
    Path("/usr/local/opt/nextcloud-micos-export"),
    Path("/etc/nextcloud-micos-export"),
    Path("/opt/nextcloud-micos-export")
]


class Settings(FileConfig, LoggerSettings, metaclass=ModelSingleton):
    class NextcloudAddressBook(BaseModel):
        url: str = Field(default=...,
                         title="Nextcloud URL",
                         description="URL to the Nextcloud server address book.")
        user: str = Field(default=...,
                          title="Nextcloud User",
                          description="User name for the Nextcloud server.")
        password: str = Field(default=...,
                              title="Nextcloud Password",
                              description="Password for the Nextcloud server.")

    micro_sip_path: FilePath = Field(default=...,
                                     title="MicroSIP Path",
                                     description="Path to the MicroSIP installation.")
    micro_sip_src_config_path: FilePath = Field(default=...,
                                                title="MicroSIP Source Config Path",
                                                description="Path to the MicroSIP source config.")
    micro_sip_src_accounts_path: list[FilePath] = Field(default_factory=list,
                                                        title="MicroSIP Source Accounts Path",
                                                        description="List of paths to the MicroSIP source accounts.")
    nextcloud_address_books: list[NextcloudAddressBook] = Field(default_factory=list,
                                                                title="Nextcloud Address Books",
                                                                description="List of Nextcloud address books.")


def settings() -> Settings:
    try:
        return Singleton.get_by_type(Settings)
    except RuntimeError:
        try:
            s = None
            for path in SETTINGS_LOOKUP_PATHS:
                file_path = path / SETTINGS_FILE_NAME
                if not file_path.is_file():
                    continue
                s = Settings(file_path=file_path, file_must_exist=True, init=True)
                break
            if s is None:
                raise FileNotFoundError(f"No '{SETTINGS_FILE_NAME}' file found. Possible paths:\n"
                                        f"{f'{chr(10)}'.join([str(path.absolute() / SETTINGS_FILE_NAME) for path in SETTINGS_LOOKUP_PATHS])}")
            return s
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)
        except ValidationError as e:
            print(e)
            sys.exit(1)
