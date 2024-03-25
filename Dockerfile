FROM python:3.10.11-slim

WORKDIR app/

RUN apt update -y && \
    apt install -y libgtk2.0-dev libglib2.0-0 libsm6 libxrender1 libxext6

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-warn-script-location --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py", "--action", "3"]
