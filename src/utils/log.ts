import { createLogger, shimLog } from '@lvksh/logger';
import { FileLogger } from '@lvksh/logger/lib/FileLog';
import chalk from 'chalk';
import { join } from 'node:path';

const date_ob = new Date();
const month = ('0' + (date_ob.getMonth() + 1)).slice(-2);
const year = date_ob.getFullYear();
const hours = date_ob.getHours();
const minutes = date_ob.getMinutes();
const seconds = date_ob.getSeconds();
const milliseconds = date_ob.getMilliseconds();

const log = createLogger(
    {
        ok: {
            label: chalk.greenBright`[OK]`,
        },
        debug: chalk.magentaBright`[DEBUG]`,
        info: {
            label: chalk.cyan`[INFO]`,
            newLine: chalk.cyan`⮡`,
            newLineEnd: chalk.cyan`⮡`,
        },
        error: chalk.bgRed.white.bold`[ERROR]`,
    },
    { padding: 'PREPEND' },
    [
        FileLogger({
            mode: 'NEW_FILE',
            path: join(__dirname + '../../', 'logs'),
            namePattern: `${year}-${month}-${hours}-${minutes}-${seconds}-${milliseconds}.txt`,
        }),
        console.log,
    ]
);

shimLog(log, 'debug');

export default log;
