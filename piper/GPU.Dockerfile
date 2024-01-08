FROM nvidia/cuda:11.8.0-devel-ubuntu22.04 as builder
ARG TARGETARCH
ARG TARGETVARIANT
ARG PIPER_OS='linux'
ARG BUILD_PIPER='yes'

# Build Piper
WORKDIR /tmp
COPY ./build_piper_src.py /tmp/build.py
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        python3 \
        python3-pip \
        git tree cmake \
        \
        build-essential \
        python3-dev \
    \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
        onnxruntime-gpu

RUN python3 /tmp/build.py


# Build final image
from nvidia/cuda:11.8.0-runtime-ubuntu22.04 as final

ARG TARGETARCH
ARG TARGETVARIANT
ARG PIPER_LIB_SRC='git+https://github.com/baudneo/wyoming-piper@usa_cuda'
ARG PIPER_OS='linux'

COPY --from=builder /tmp/piper /usr/share/piper

WORKDIR /
RUN \
    env \
    \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        python3 \
        python3-pip \
        git \
    \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
        onnxruntime-gpu \
    \
    && pip3 install --no-cache-dir \
        "${PIPER_LIB_SRC}" \
    \
    && apt-get purge -y --auto-remove \
        git \
    && rm -rf /var/lib/apt/lists/*

COPY ./run-gpu.sh /

EXPOSE 10200

ENTRYPOINT ["bash", "/run-gpu.sh"]
