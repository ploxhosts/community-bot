# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY . .


RUN apt-get update
RUN apt-get install tesseract-ocr
RUN apt-get install libtesseract-dev

# install dependencies
RUN pip install -r requirements.txt


# command to run on container start
CMD [ "python", "./main.py", "&&", "curl", "mongodb:27017"]