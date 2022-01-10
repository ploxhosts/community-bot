import postgres from '../postgres';
import log from '../../utils/log';

export const addBadWord = (badWord: string, guild_id: string) => {
  return postgres.query(
    `INSERT INTO ploxy_badwords (word) WHERE guild_id = $2 VALUES ($1)`,
    [badWord, guild_id]
  );
}

export const removeBadWord = (badWord: string, guild_id: string) => {
  return postgres.query(
    `DELETE FROM ploxy_badwords WHERE word = $1 WHERE guild_id = $2`,
    [badWord, guild_id]
  );
}

export const getAllBadWords = (guild_id: string) => {
  return postgres.query(
    `SELECT word FROM ploxy_badwords WHERE guild_id = $1`,
    [guild_id]
  );
}

export const getAll = (guild_id: string) => {
  return postgres.query(
    `SELECT * FROM ploxy_badwords WHERE guild_id = $1`,
    [guild_id]
  );
}