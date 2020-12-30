# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY ./requirements.txt .

# copy the prepare file to the working directory
COPY prepare.py .

# copy the license file to the working directory
COPY LICENSE .

# copy the jokes json file to the working directory
COPY jokes.json .

# copy the env file to the working directory
COPY .env .

# copy the content of the local cogs directory to the working directory
COPY cogs/ ./cogs/

# copy the main file to the working directory
COPY main.py .

# install dependencies
RUN pip install -r requirements.txt



# command to run on container start
CMD [ "python", "./main.py", "&&", "curl", "mongodb:27017"]