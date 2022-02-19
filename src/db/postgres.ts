import { promises as fs } from 'node:fs';
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
    // eslint-disable-next-line unicorn/no-process-exit
    process.exit(-1);
});

export const updateTables = async () => {
    const files: { [name: string]: string } = {};

    console.log('Checking for new db tables');

    for (const file of await fs.readdir(__dirname + '/tables')) {
        if (file.slice(-4) === '.sql') {
            // Only js files and not test.js
            await fs
                .readFile(__dirname + '/tables/' + file, 'utf8')
                .then((data) => {
                    files[file.slice(0, -4)] = data;
                });
        }
    }
    const tables = Object.keys(files);

    // Now that we have collected all the tests, run them.
    tables
        .sort((a, b) => {
            return a.localeCompare(b); // Sorting out by number 1 will go infront of 2
        })
        // eslint-disable-next-line unicorn/no-array-for-each
        .forEach(async (key) => {
            console.log(key);

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
