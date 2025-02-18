FROM debian:bullseye-slim
ARG TARGETARCH
ARG TARGETVARIANT

# Install Piper
WORKDIR /usr/src
ARG PIPER_LIB_VERSION='1.4.0'
ARG PIPER_RELEASE='v1.2.0'

RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        python3 \
        python3-pip \
    \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
    && pip3 install --no-cache-dir \
        "wyoming-piper==${PIPER_LIB_VERSION}" \
    \
    && curl -L -s \
        "https://github.com/rhasspy/piper/releases/download/${PIPER_RELEASE}/piper_${TARGETARCH}${TARGETVARIANT}.tar.gz" \
        | tar -zxvf - -C /usr/share \
    \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /
COPY run-nongpu.sh ./

EXPOSE 10200

ENTRYPOINT ["bash", "/run-nongpu.sh"]
