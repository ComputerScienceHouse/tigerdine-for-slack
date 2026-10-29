FROM python:3.15-slim-trixie

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

WORKDIR /srv/tigerdine-slack

RUN pip install --upgrade pip

COPY requirements.txt /srv/tigerdine-slack

RUN pip install -r requirements.txt

COPY . /srv/tigerdine-slack

ENTRYPOINT ["python3", "bot.py"]
