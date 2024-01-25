FROM nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04

ARG INSTALL_WHISPER_SRC="git+https://github.com/baudneo/wyoming-faster-whisper.git@hf_asr_models"
#ARG INSTALL_WHISPER_SRC="git+https://github.com/rhasspy/wyoming-faster-whisper"
# Install Whisper
WORKDIR /usr/src
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3 \
        python3-dev \
        python3-pip \
        git \
    \
    && pip3 install --no-cache-dir -U \
        setuptools \
        wheel \
    && pip3 install --no-cache-dir \
        "${INSTALL_WHISPER_SRC}" \
    \
    && apt-get purge -y --auto-remove \
        build-essential \
        python3-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /
COPY run.sh ./

EXPOSE 10300

ENTRYPOINT ["bash", "/run.sh"]
