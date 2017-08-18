FROM python:alpine

# copy and install our ballast library
ADD setup.py README.rst /app/
ADD ballast /app/ballast/
RUN pip install -e ./app/

# copy our example app
ADD examples/eureka/client/app.py /app/

CMD ["python", "./app/app.py"]