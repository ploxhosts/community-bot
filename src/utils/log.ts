import { createLogger, shimLog } from '@lvksh/logger';
import { FileLogger } from '@lvksh/logger/lib/FileLog';
import chalk from 'chalk';
import { join } from 'path';

let date_ob = new Date();
let month = ("0" + (date_ob.getMonth() + 1)).slice(-2);
let year = date_ob.getFullYear();
let hours = date_ob.getHours();
let minutes = date_ob.getMinutes();
let seconds = date_ob.getSeconds();
let milliseconds = date_ob.getMilliseconds();

const log = createLogger(
  {
    ok: {
        label: chalk.greenBright`[OK]`
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
  [FileLogger({
      mode: 'NEW_FILE',
      path: join(__dirname, 'logs'),
      namePattern: `${year}-${month}-${hours}-${minutes}-${seconds}-${milliseconds}.txt`,
  }), console.log]
);

shimLog(log, 'debug');

export default log;