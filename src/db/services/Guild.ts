import postgres from '../postgres';
import log from '../../utils/log';
import { RedisClientType } from 'redis';

let redis: RedisClientType;
/**
 * @param {string} guild_id - The guild id
 * @param {string} guild_name - The guild name
 * @param {string} avatar - The guild logo image, link to the cdn
 * @param {string} owner_id - The user id of the person who owns the server
 * @param {number} premium - What boost level is the server, 0 is no boosts
 * @param {number} banned - Are they banned from using the bot like a rate limit, 0 is default
 * @param {number} payment_level - What payment level is the server, 0 is default
 * @param {boolean} listing - Whether the server is listed or not, 0 is default
 * @param {boolean} has_setup - Whether the server has setup the bot or not, 0 is default
 * @param {boolean} support_packages_enabled - Whether the server has enabled support packages or not, 0 is default
 * @param {boolean} auto_support_enabled - Whether the server has enabled auto support or not, 0 is default
 * @description Creates a guild
**/

export const createGuild = async (
  guild_id: string, 
  guild_name: string, 
  avatar: string | null,
  owner_id: string,
  premium: number,
  banned: number = 0,
  payment_level: number = 0,
  listing: boolean = false,
  has_setup: boolean = false,
  support_packages_enabled: boolean = false,
  auto_support_enabled: boolean = false
  ) => {
  if (await getGuild(guild_id)) {
    log.debug(`Guild ${guild_id} already exists, createGuild failed`);
    return false;
  }
  const query = `INSERT INTO ploxy_guilds (
    guild_id,
    guild_name,
    avatar,
    owner_id,
    premium,
    banned,
    payment_level,
    listing,
    has_setup,
    support_packages_enabled,
    auto_support_enabled
  ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)`;
  const values = [
    guild_id,
    guild_name,
    avatar,
    owner_id,
    premium,
    banned,
    payment_level,
    listing,
    has_setup,
    support_packages_enabled,
    auto_support_enabled
  ];
  try {
    const res = await postgres.query(query, values);
    await redis.set(`guild:${guild_id}`, JSON.stringify(res.rows[0]));
    return res.rows[0];
  } catch (err: any) {
    log.error(err);
    return false;
  }

}

/**
 * @param {string} guild_id - The guild id
 * 
 * @description Gets a guild
*/

export const getGuild = async (guild_id: string) => {
  const query = `SELECT * FROM ploxy_guilds WHERE guild_id = $1`;
  const values = [guild_id];
  try {
    const guildCache = await redis.get(`guild:${guild_id}`);
    if (guildCache) {
      return JSON.parse(guildCache);
    }
    const res = await postgres.query(query, values);
    await redis.set(`guild:${guild_id}`, JSON.stringify(res.rows[0]));
    return res.rows[0];
  } catch (err: any) {
    log.error(err);
    return false;
  }
}


/**
 * 
 * @description Gets all guilds
*/

export const getAllGuild = async () => {
  const query = `SELECT * FROM ploxy_guilds`;
  try {
    const guildCache = await redis.get(`guild:${guild_id}`);
    if (guildCache) {
      return JSON.parse(guildCache);
    }
    const res = await postgres.query(query);
    res.rows.forEach(async (guild: any) => {
      await redis.set(`guild:${guild.guild_id}`, JSON.stringify(guild));
    });
    return res.rows;
  } catch (err: any) {
    log.error(err);
    return false;
  }
}

/**
 * @param {string} guild_id - The guild id
 * @param {string} guild_name - The guild name
 * @param {string} avatar - The guild logo image, link to the cdn
 * @param {string} owner_id - The user id of the person who owns the server
 * @param {number} premium - What boost level is the server, 0 is no boosts
 * @param {number} banned - Are they banned from using the bot like a rate limit, 0 is default
 * @param {number} payment_level - What payment level is the server, 0 is default
 * @param {boolean} listing - Whether the server is listed or not, 0 is default
 * @param {boolean} has_setup - Whether the server has setup the bot or not, 0 is default
 * @param {boolean} support_packages_enabled - Whether the server has enabled support packages or not, 0 is default
 * @param {boolean} auto_support_enabled - Whether the server has enabled auto support or not, 0 is default
 * @description Updates a guild
**/


export const updateGuild = async (
  guild_id: string, 
  guild_name: string, 
  avatar: string,
  owner_id: string,
  premium: number,
  banned: number = 0,
  payment_level: number = 0,
  listing: boolean = false,
  has_setup: boolean = false,
  support_packages_enabled: boolean = false,
  auto_support_enabled: boolean = false
  ) => {
  const query = `UPDATE ploxy_guilds SET
    guild_name = $2,
    avatar = $3,
    owner_id = $4,
    premium = $5,
    banned = $6,
    payment_level = $7,
    listing = $8,
    has_setup = $9,
    support_packages_enabled = $10,
    auto_support_enabled = $11
  WHERE guild_id = $1`;
  const values = [
    guild_id,
    guild_name,
    avatar,
    owner_id,
    premium,
    banned,
    payment_level,
    listing,
    has_setup,
    support_packages_enabled,
    auto_support_enabled
  ];
  try {
    const res = await postgres.query(query, values);
    await redis.set(`guild:${guild_id}`, JSON.stringify(res.rows[0]));
    return res.rows[0];
  } catch (err: any) {
    log.error(err);
    return false;
  }
}

/**
 * @param {string} guild_id - The guild id
 * 
 * @description Deletes a guild
*/

export const deleteGuild = async (guild_id: string) => {
  const query = `DELETE FROM ploxy_guilds WHERE guild_id = $1`;
  const values = [guild_id];
  try {
    await redis.del(`guild:${guild_id}`);
    const res = await postgres.query(query, values);
    return res.rows[0];
  } catch (err: any) {
    log.error(err);
    return false;
  }
}

module.exports = {
  setRedis: function(redis: RedisClientType) {
    redis = redis;
  }
}
