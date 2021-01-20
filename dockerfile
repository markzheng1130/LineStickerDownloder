FROM python:3.8-slim
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
ENV FLASK_DEBUG=1
CMD python flasky.py
