import {config} from 'dotenv'
import path from 'path';
config({ path: path.join(__dirname, ".env") });

const env = {
    token: process.env.token as string,
    prefix: process.env.prefix as string || "?",
    guildId: process.env.guildId as string,
    clientId: process.env.clientId as string,
    MYSQL_host: process.env.MYSQL_host as string,
    MYSQL_port: process.env.MYSQL_port as string,
    MYSQL_DATABASE: process.env.MYSQL_DATABASE as string,
    MYSQL_USER: process.env.MYSQL_USER as string,
    MYSQL_PASSWORD: process.env.MYSQL_PASSWORD as string,
    MYSQL_ROOT_PASSWORD: process.env.MYSQL_ROOT_PASSWORD as string,
    themeColor: process.env.themeColor as string,
    brandName: process.env.brandName as string
}

export default env
