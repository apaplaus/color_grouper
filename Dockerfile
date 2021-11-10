FROM python:3

WORKDIR /src

COPY config.cfg /etc/color_grouper/

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir . --no-deps

ENTRYPOINT [ "/bin/sh" ]
