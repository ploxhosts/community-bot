import mysql from 'mysql';

const connection: mysql.Pool = mysql.createPool({
	connectionLimit: 50,
	host: process.env.mysql_host as string,
	user: process.env.MYSQL_USER as string,
	password: process.env.MYSQL_PASSWORD as string,
	database: process.env.MYSQL_DATABASE as string,
});

export default connection;
