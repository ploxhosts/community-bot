# set base image (host OS)
FROM node:16

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY . .


RUN apt-get update
RUN apt-get install tesseract-ocr -y
RUN apt-get install libtesseract-dev -y
RUN apt-get install ffmpeg libsm6 libxext6 libgl1-mesa-dev -y


# install dependencies and get ride of cache
RUN npm ci --only=production && npm cache clean --force

ENV docker true
ENV NODE_ENV production

# command to run on container start
CMD [ "npm", "run", "prod"]
