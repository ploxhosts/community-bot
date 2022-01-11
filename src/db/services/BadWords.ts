import postgres from '../postgres';
import log from '../../utils/log';
import { RedisClientType } from 'redis';

let redis: RedisClientType;

/**
 * Adds a guild bad word
 *
 * @param badWord - The bad word to be stored Example cake
 * @param guild_id - The user id Example 1232132132131231
 *
 */
export const addBadWord = (badWord: string, guild_id: string) => {
  try {
    return postgres.query(
      `INSERT INTO ploxy_badwords (word) WHERE guild_id = $2 VALUES ($1)`,
      [badWord, guild_id]
    );
  } catch (error: any) {
    log.error(error);
    return false;
  }
}

/**
 * Removes a bad word from a guild
 *
 * @param badWord - The bad word to be stored Example cake
 * @param guild_id - The user id Example 1232132132131231
 *
 */

export const removeBadWord = (badWord: string, guild_id: string) => {
  try {
    return postgres.query(
      `DELETE FROM ploxy_badwords WHERE word = $1 WHERE guild_id = $2`,
      [badWord, guild_id]
    );
  } catch (error: any) {
    log.error(error);
    return false;
  }
}

/**
 * Gets all badwords from a guild
 *
 * @param guild_id - The user id Example 1232132132131231
 *
 */

export const getAllBadWords = (guild_id: string) => {
  try {
    return postgres.query(
      `SELECT word FROM ploxy_badwords WHERE guild_id = $1`,
      [guild_id]
    );
  } catch (error: any) {
    log.error(error);
    return false;
  }
}

/**
 * Gets all data from a guild
 *
 * @param guild_id - The user id Example 1232132132131231
 *
 */

export const getAll = (guild_id: string) => {
  try {
    return postgres.query(
      `SELECT * FROM ploxy_badwords WHERE guild_id = $1`,
      [guild_id]
    );
  } catch (error: any) {
    log.error(error);
    return false;
  }
}

module.exports = {
  setRedis: function(redis: RedisClientType) {
    redis = redis;
  }
}