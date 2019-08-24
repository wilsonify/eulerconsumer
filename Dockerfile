FROM python:3.7-alpine
ADD . /code
WORKDIR /code
RUN chmod 644 /code/app.py
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
EXPOSE 5000
