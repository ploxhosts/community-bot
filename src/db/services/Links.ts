import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';

let redis: RedisClientType;

/**
 * Adds a link
 *
 * @param link- The link to be stored Example https://example.com
 * @param addedBy - The user id Example 1232132132131231
 * @param score - The threat level
 * @param process - the logs of what happened to gain score
 * @param guild_id - The guild id that set the link or set undefined if done by system
 *
 *
 */
export const addLink = async (
    link: string,
    addedBy: string | undefined,
    score: number,
    process: { type: string; score: number }[],
    guildId: string | undefined,
    allowed: boolean
) => {
    try {
        const result = await postgres.query(
            'INSERT INTO ploxy_links (link, added_by, score, process, guild_id, allowed) VALUES ($1, $2, $3, $4, $5)',
            [link, addedBy, score, process.toString(), guildId, allowed]
        );

        await redis.set(
            `link:${link}:${guildId}`,
            JSON.stringify(result.rows.at(0))
        );
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * Removes a link
 *
 * @param link - The link to be stored Example https://example.com
 * @param guildId - The guild id that set the link or set undefined if done by system
 */

export const removeLink = async (link: string, guildId: string | undefined) => {
    try {
        await postgres.query(
            'DELETE FROM ploxy_links WHERE link = $1 AND guild_id = $2',
            [link, guildId]
        );

        return await redis.del(`link:${link}:${guildId}`);
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * Check a link
 *
 */

export const checkLink = async (
    link: string,
    guildId: string | undefined
): Promise<any> => {
    try {
        const redisResult = await redis.get(`link:${link}:${guildId}`);

        if (redisResult) {
            return JSON.parse(redisResult);
        }

        const result = await postgres.query(
            'SELECT * FROM ploxy_links WHERE link = $1 AND guild_id = $2',
            [link, guildId]
        );

        if (result.rowCount > 0) {
            return result.rows.at(0);
        }

        return false;
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * Gets all links
 *
 */

export const getAllLinks = async () => {
    try {
        return await postgres.query('SELECT * FROM ploxy_links');
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * Gets all links based on guildId
 *
 * @param guildId - The guild id that set the link or set undefined if done by system
 */

export const getAllLinksByGuildId = async (guildId: string) => {
    try {
        return await postgres.query(
            'SELECT * FROM ploxy_links WHERE guild_id = $1',
            [guildId]
        );
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

module.exports = {
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
    getAllLinks,
    removeLink,
    addLink,
    getAllLinksByGuildId,
};
