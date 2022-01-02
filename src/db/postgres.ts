import pg from 'pg';
import log from '../utils/log';

const pool = new pg.Pool({
	max: 25,
	host: process.env.mysql_host as string,
	user: process.env.MYSQL_USER as string,
	password: process.env.MYSQL_PASSWORD as string,
	database: process.env.MYSQL_DATABASE as string,
  idleTimeoutMillis: 30000
});


pool.on('error', (err, client) => {
  log.error("Unexpected error on postgres connection", err);
  process.exit(-1)
})

pool.on('connect', client => {
  log.ok("Connected to postgres database");
})

export default pool;
