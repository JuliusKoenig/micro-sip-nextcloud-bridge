FROM python:3.12-slim

ENV MICRO_SIP_NEXTCLOUD_BRIDGE_ADDRESS_BOOKS="[{\"url\":\"https://cloud.example.de/remote.php/dav/addressbooks/users/exampleuser/adressbuch_shared_by_admin\",\"user\":\"exampleuser\",\"password\":\"xxx\"}]"
ENV MICRO_SIP_NEXTCLOUD_BRIDGE_LOG_LEVEL=INFO
ENV MICRO_SIP_NEXTCLOUD_BRIDGE_SERVER_HOST="0.0.0.0"
ENV MICRO_SIP_NEXTCLOUD_BRIDGE_SERVER_PORT=8123

EXPOSE ${MICRO_SIP_NEXTCLOUD_BRIDGE_SERVER_PORT}

COPY ./ /app
WORKDIR /app

RUN pip install -e .

CMD ["micro-sip-nextcloud-bridge-server"]