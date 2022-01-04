import pg from 'pg';
import log from '../utils/log';
import {fs} from 'fs';

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

  fs.readdir(__dirname + '/db/tables', function (err, files) {
    //handling error
    if (err) {
      return console.log("\x1b[31m"+ 'Unable to scan directory in attempt to load sql tables: ' + err + "\x1b[0m");
    } 
    //listing all files using forEach
    files.forEach(function (file) {
      fs.readFile(__dirname + '/db/tables/' + file, 'utf8', function (err, data) {
        if (err) {
          return console.log("\x1b[31m"+ 'Unable to read file: ' + err + "\x1b[0m");
        }
        connection.query(data, function (err, result) { // Run whatever is in the sql file
          if (err) {
            return console.log("\x1b[31m"+ 'Unable to run query: ' + err + "\x1b[0m");
          }
        });
      });
    });
    // TODO: Create a patches folder within the db folder and put all sql files to update the database in there. Sort of similar to 00-thefirstupdate.sql and 01-thesecondupdate.sql
    // TODO: Loop through patches
  });
})

export default pool;
