import fs from 'node:fs';
import pg from 'pg';

import log from '../utils/log';

const pool = new pg.Pool({
    max: 25,
    host: process.env.POSTGRES_HOST as string,
    user: process.env.POSTGRES_USER as string,
    password: process.env.POSTGRES_PASSWORD as string,
    database: process.env.POSTGRES_DATABASE as string,
    idleTimeoutMillis: 30_000,
});

pool.on('error', (error, client) => {
    log.error('Unexpected error on postgres connection', error);
    process.exit(-1);
});

export const updateTables = async () => {
    const files: { [name: string]: string } = {};

    console.log('Checking for new db tables');

    for (const file of fs.readdirSync(__dirname + '/tables')) {
        if (file.slice(-3) === '.sql') {
            // Only js files and not test.js

            files[file] = require('./' + file);
        }
    }

    // Now that we have collected all the tests, run them.
    Object.keys(files)
        .sort((a, b) => {
            return a.localeCompare(b); // Sorting out by number 1 will go infront of 2
        })
        .forEach(async (key) => {
            for (const line of files[key].split(';')) {
                try {
                    await pool.query(line);
                } catch (error: any) {
                    if (!error.message.includes('already exists')) {
                        log.error(error);
                    }
                }
            }
        });

    console.log('Finished looking for new tables');

    // TODO: Create a patches folder within the db folder and put all sql files to update the database in there. Sort of similar to 00-thefirstupdate.sql and 01-thesecondupdate.sql
    // TODO: Loop through patches
};

export default pool;
