FROM python:3.7.7-alpine3.11 as base

FROM base as builder

RUN mkdir /install
RUN /bin/sh -c 'apk update && apk add --no-cache postgresql-dev gcc musl-dev geos-dev linux-headers libffi-dev openssl-dev python3-dev git'
COPY requirements.txt /install/requirements.txt
RUN /bin/sh -c 'pip3 install --no-cache-dir --upgrade pip'
RUN /bin/sh -c 'pip3 install --no-warn-script-location --no-cache-dir --prefix /install -r /install/requirements.txt'
RUN /bin/sh -c 'pip3 install --no-warn-script-location --no-cache-dir --prefix /install setproctitle'
RUN /bin/sh -c 'apk add --update npm && npm install -g bower'

COPY bowerapp .bowerrc bower.json /

RUN /bin/sh -c 'bower --allow-root install'

FROM base

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

COPY --from=builder /install /usr/local

RUN /bin/sh -c 'apk update && apk add --no-cache postgresql-dev geos'

WORKDIR /app
RUN mkdir /app/staticfiles
RUN mkdir /app/mediafiles

# copy project files on /app folder
COPY . .

COPY --from=builder /bowerapp/static/components bowerapp/static/components

EXPOSE 8000
ENTRYPOINT ["/bin/sh", "docker/entrypoint.sh"]