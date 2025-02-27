from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from wiederverwendbar.logger import LoggerSettings
from wiederverwendbar.uvicorn import UvicornServerSettings


class Settings(BaseSettings, UvicornServerSettings, LoggerSettings):
    model_config = {
        "env_prefix": "MICRO_SIP_NEXTCLOUD_BRIDGE_",
        "case_sensitive": False
    }

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
        country_code: str = Field(default="+49",
                                  title="Country Code",
                                  description="Country code for the Nextcloud server.")

    address_books: list[NextcloudAddressBook] = Field(default_factory=list,
                                                      title="Nextcloud Address Books",
                                                      description="List of Nextcloud address books.")
    use_cached_contacts: bool = Field(default=False,
                                      title="Use Cached Contacts",
                                      description="Use cached contacts instead of fetching them from the Nextcloud server.")
    contacts_update_interval: int = Field(default=900,
                                          title="Contacts Update Interval in Seconds",
                                          description="Interval in seconds for updating contacts.")
