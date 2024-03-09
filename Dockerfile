FROM python:3.10.11-alpine3.18

WORKDIR app/

RUN apt update && apt install nodejs && apt install npm -y \
    && rm -rf /var/lib/apt/lists/* \

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-warn-script-location --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py", "--action", "3"]