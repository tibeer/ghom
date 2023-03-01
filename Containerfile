FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ghom /usr/local/lib/python3.10/site-packages/ghom

ENTRYPOINT ["/usr/local/bin/python", "-m", "ghom.main"]
