# community-bot

An open sourced community projected created for our discord server. 
![Total file size](https://img.shields.io/github/languages/code-size/PloxHost-LLC/community-bot) ![File count](https://img.shields.io/github/directory-file-count/PloxHost-LLC/community-bot) ![Python version](https://img.shields.io/badge/python-v3.8-blue)

# PloxHost Community Bot

An open source bot written for the community by the community. The project is planned and maintained by FluxedScript and Mark D.

## Why an open source community bot?

There is need for a dedicated bot in the main server. Many people need a discord bot you can get rewards from. We could've gone with an approach like all other bot developers do and make it closed source, but we went with an open source approach.

If there is a bug, **you** can change it if you want. If you want something, **you** can add it. There are little restrictions as long as an issue is created and approved you can make it - we don't want you wasting time.

## Why contribute?

After successfully contributing time and effort to the community bot by either making the code cleaner, adding new changes, fixing bugs, adding language support or spelling and grammar changes. You might **receive** a role as a **reward**. The features of this role would be a special colour and economy system rewards and more to come as time moves on.

## Steps to contribute

Firstly you need to install python 3.8. This can be downloaded from https://python.org for your operating system.

You will also need to have git installed.

You need to make a Fork of the current repository and then clone it to your system(downloading it)

Now you have the code locally and have the ability to test it. You must make a mongodb database either on the official website or using a docker image(recommended).

You must have docker and docker compose for the docker related setup. Appropriate files are in the main directory.

Now you must install all the dependencies in requirements.txt using `pip install -r requirements.txt`

You must create a file named `.env` with the contents of the template file. Fill in with the correct details and save.

You can now run the code using `python main.py` in the command line or by pressing run in your ide.

Now you can commit and push to your repository or continue to make changes. All features need to meet a few requirements before being added, but those are in the heading named `steps before contributing` but once met you can open a pull request and wait for an answer.

## Steps before contributing

- The code must all be working, running the command should work without errors, obvious errors should be corrected such as taking money when adding money.

- The code must not change the .env file unless authorised by a maintainer.

- All new features/large changes must have an issue created. This issue would contain the benefits/uses of having such a change and trying to convince others to support it.

- The code must not use any 3rd party api unless allowed by PloxHost management.

- The code must not be malicious/harmful. Code that is written in a way where it risks exposing the database(No SQL injection), insecure admin commands(banning without appropriate permissions) and/or creating anything illegal will not be allowed.

- Finally, be nice and leave a few comments here and there. Think "what is my thinking process" and just write it down. Keep them short but being funny is allowed.

## What if I need help to contribute?

`/cogs/example.py` contains everything you need to get started with a new cog. From deleting data to making data it has it all.

### Want to help people with bot development? 

Feel free to update the example.py cog with additional helpful information/comments.


