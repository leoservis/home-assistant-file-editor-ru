ARG BUILD_FROM=ghcr.io/home-assistant/base:3.24-2026.10.1@sha256:992dc6a5727b97a30da8dd259b489739299c324407557df540165e2f0dbb7763
FROM $BUILD_FROM

ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN apk add --no-cache git openssh-client py3-pip python3

COPY hass_configurator /tmp/hass-configurator
RUN pip3 install /tmp/hass-configurator \
    && find /usr/local \
        \( -type d -a -name test -o -name tests -o -name '__pycache__' \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' +

COPY rootfs /

HEALTHCHECK --start-period=30s --start-interval=5s --interval=30s \
    CMD curl --fail http://127.0.0.1:8099 || exit 1

LABEL \
    org.opencontainers.image.title="Home Assistant App: File editor (Russian)" \
    org.opencontainers.image.description="Russian interface for the Home Assistant File editor app" \
    org.opencontainers.image.source="https://github.com/leoservis/home-assistant-file-editor-ru" \
    org.opencontainers.image.licenses="Apache-2.0"
