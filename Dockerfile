#base image
FROM python:3.10-slim  

# set environment variables
RUN apt update -y && apt install awscli -y
WORKDIR /app
# install dependencies
COPY . /app
RUN pip install  -r requirements.txt


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
