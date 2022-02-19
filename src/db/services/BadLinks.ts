import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';

let redis: RedisClientType;

/**
 * Adds a bad link
 *
 * @param badLink- The bad link to be stored Example https://example.com
 * @param addedBy - The user id Example 1232132132131231
 * @param score - The threat level
 *
 */
export const addBadLink = async (
    badLink: string,
    addedBy: string,
    score: number
) => {
    try {
        return await postgres.query(
            'INSERT INTO ploxy_badlinks (link, added_by, score) VALUES ($1, $2, $3)',
            [badLink, addedBy, score]
        );
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * Removes a bad link
 *
 * @param badLink - The bad link to be stored Example https://example.com
 *
 */

export const removeBadLink = async (badLink: string) => {
    try {
        return await postgres.query(
            'DELETE FROM ploxy_badlinks WHERE link = $1',
            [badLink]
        );
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * Gets all badlinks
 *
 */

export const getAllBadLinks = async () => {
    try {
        return await postgres.query('SELECT * FROM ploxy_badlinks');
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

module.exports = {
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
    getAllBadLinks,
    removeBadLink,
    addBadLink,
};
