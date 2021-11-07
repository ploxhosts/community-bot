# PloxHost Community Bot - Ploxy

An open-source community project created by members of our discord server, maintained by FluxedScript, developed for your community.

![Total file size](https://img.shields.io/github/languages/code-size/PloxHost-LLC/community-bot)

## 🏗️ Requirements

1. [A Discord Bot Token](https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot)
2. [Node.js v16.6 or newer](https://nodejs.org/en/download/)
3. A mysql/mariadb server with access to a database.
4. **(Optional)** [Docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/) installed.

## ⚙️Configuration

Copy/rename `.env-template` to `.env` and fill out the values:

### ⚠️ Never commit or share your token or API keys publicly ⚠️

```env
token = token
prefix = ?
guildId = main_guild_id
clientId = bot_id
mysql_host="localhost"
mysql_port=3306
mysql_username="username"
mysql_password="password"
mysql_database="database"
themeColor = "#39b5af"
brandName = "Ploxy"
```

**Step 1:** Replace `token` with your bot token such as `eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U`. After doing so, you will end up with `token = eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U`. **This is not your token**, to get one please follow this [guide](https://discordjs.guide/preparations/setting-up-a-bot-application.html#creating-your-bot).

**Step 2:** Decide on a prefix for administrative commands such as changing bot features. All public-facing features use [slash commands](https://support.discord.com/hc/en-us/articles/1500000368501-Slash-Commands-FAQ).

**Step 3:** Get your test guild's id to publish guild specific commands for testing. The guild id can be obtained by following this [guide](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-).

**Step 4:** Decide on MySQL/MariaDB details. If using Discord Bot hosting offered by PloxHost, please navigate to your bot -> Databases -> Click on your database or create one(pick any name). If you

- `mysql_host` is the endpoint, whether it is a Domain or an IP address. If you are using a localhost database put `172.0.0.1` or `localhost`.

- `mysql_port` is the MySQL/MariaDB port. The default is `3306`.

- `mysql_username` is the MySQL/MariaDB username you want to use. On PloxHost's panel, it is the long name on the right side of the database. Place this in quotations to avoid any issues.

- `mysql_password` is the MySQL/MariaDB password you want to use. On PloxHost's panel, it's the eye next to the garbage bin emoji, press the eye and scroll down till you see the password field.

- `mysql_database` is the MySQL/MariaDB database name you want to use. On PloxHost's panel, it's the large text on the left side. Make sure the user has the correction permissions to access the database.

**Step 5:** Setup brand information for your bot.

- `themeColor` is the embed colour theme to use. This can be any hex string that you want to use. You could use the help of a colour wheel or use your brand [colour](https://www.canva.com/colors/color-wheel/).

- `brandName` is what will show up on the bottom of embeds. You could use the name of your brand or bot.

## ▶️ Running the bot

You can run the bot with different methods. The most recommended one is to use docker as most things are done for you.

### 🖥️ Development Configuration

*made for writing and testing code*

To run it on your own computer do `npm install` then `npm run dev` in the directory of the project.

If you want to a run more production version of the bot use `npm install` then `npm run build` then `npm run start`.

### 🐬 Docker Configuration

*made for production/hosting it*

Navigate to the project directory and run the following command:

```bash
docker-compose up --detach
```

### 🗄️ Dicord Bot Hosting Configuration

*made for running it on a discord bot hosting*

Navigate to the project directory and run `npm run build`.

Copy all the files to your host using sftp/ftp. It is recommended to host this on a VPS/KVM instead.

## 🤝 Contributing

Read the [CONTRIBUTING.md](https://github.com/PloxHost-LLC/community-bot/blob/discord.js/CONTRIBUTING.md) for details on how to contribute to this project.
