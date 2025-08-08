FROM python:3.13-slim

WORKDIR /web_application

COPY ../requirements.txt ./requirements.txt
COPY ../python-style ./python-style
COPY ../front-init ./front-init

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000
EXPOSE 5000

CMD ["python", "python-style/main.py"]
