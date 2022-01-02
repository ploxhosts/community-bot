import postgres from '../db/postgres';

export async function checkDatabaseConnection(connection: string,) {
  postgres.connect(connection, (err) => {
    if (err) {
      console.log('Error connecting to postgres database: ', err);
      return false;
    }
    console.log('Connected to postgres database');
    return true;
  }
}