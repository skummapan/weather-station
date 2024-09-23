FROM python:3.12-bookworm

RUN apt-get update && apt-get install -y locales && \
    sed -i '/sv_SE.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen

ENV LANG=sv_SE.UTF-8
ENV LANGUAGE=sv_SE:sv
ENV LC_ALL=sv_SE.UTF-8

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN locale-gen sv_SE.utf8

WORKDIR /app
RUN mkdir -p /app

COPY ./src /app

# ENTRYPOINT ["pip", "freeze"]
# ENTRYPOINT ["which", "python3"]
ENTRYPOINT ["/usr/local/bin/python3", "/app/__main__.py"]
