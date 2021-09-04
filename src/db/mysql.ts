import mysql from 'mysql';

const connection: mysql.Pool = mysql.createPool({
	connectionLimit: 50,
	host: process.env.mysql_host as string,
	user: process.env.mysql_username as string,
	password: process.env.mysql_password as string,
	database: process.env.mysql_database as string,
});

export default connection;
