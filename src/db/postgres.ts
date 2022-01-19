import pg from 'pg';
import log from '../utils/log';
import fs from 'fs';

const pool = new pg.Pool({
	max: 25,
	host: process.env.POSTGRES_HOST as string,
	user: process.env.POSTGRES_USER as string,
	password: process.env.POSTGRES_PASSWORD as string,
	database: process.env.POSTGRES_DATABASE as string,
  idleTimeoutMillis: 30000
});


pool.on('error', (err, client) => {
  log.error("Unexpected error on postgres connection", err);
  process.exit(-1)
})

const arrayRemove = (arr: string[], value: string) => { 
    
  return arr.filter(function(ele){ 
      return ele != value; 
  });
}

export const updateTables = async () => {
  let files: {[name: string]: string;} = {}

  console.log("Checking for new db tables")
  fs.readdirSync(__dirname + '/tables').forEach(file => {
    if (file.slice(-3) === ".sql") { // Only js files and not test.js

      files[file] = require("./" + file);
    }
  });
  
  // Now that we have collected all the tests, run them.
  Object.keys(files).sort(function(a, b) { 
    return a.localeCompare(b); // Sorting out by number 1 will go infront of 2
  }).forEach(async function(key) {
    for (const line of files[key].split(";")) {
      try {
        await pool.query(line);
      } catch (e: any) {
        if (!e.message.includes("already exists")){
          log.error(e);
        }
      }
    }
  });
  
  console.log("Finished looking for new tables")

  
  // TODO: Create a patches folder within the db folder and put all sql files to update the database in there. Sort of similar to 00-thefirstupdate.sql and 01-thesecondupdate.sql
  // TODO: Loop through patches
}

export default pool;
