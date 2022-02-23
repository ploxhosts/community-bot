import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';

let redis: RedisClientType;

interface BadWordData {
    word_id: string,
    guild_id: string,
    word: string,
    implicit: boolean,
    created_at: string,
    updated_at: string,
    created_by: string,
}
class BadWords{
    /**
     * Adds a guild bad word
     *
     * @param badWord - The bad word to be stored Example cake
     * @param guild_id - The user id Example 1232132132131231
     *
     */
    addBadWord = async (badWord: string, guild_id: string): Promise<BadWordData | false> => {
        try {
            const result = await postgres.query(
                'INSERT INTO ploxy_badwords (word) WHERE guild_id = $2 VALUES ($1)',
                [badWord, guild_id]
            );
            return result.rows.at(0) as BadWordData;
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };

    /**
     * Removes a bad word from a guild
     *
     * @param badWord - The bad word to be stored Example cake
     * @param guild_id - The user id Example 1232132132131231
     *
     */

    removeBadWord = async (badWord: string, guild_id: string): Promise<BadWordData | false> => {
        try {
            const result = await postgres.query(
                'DELETE FROM ploxy_badwords WHERE word = $1 WHERE guild_id = $2',
                [badWord, guild_id]
            );
            return result.rows.at(0) as BadWordData;
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };


    /**
     * Gets all badwords from a guild
     *
     * @param guild_id - The user id Example 1232132132131231
     *
     */
    getAllBadWords = async (guild_id: string): Promise<BadWordData[] | false> => {
        try {
            const result = await postgres.query(
                'SELECT word FROM ploxy_badwords WHERE guild_id = $1',
                [guild_id]
            );
            return result.rows;
        } catch (error: any) {
            log.error(error);
    
            return false;
        }
    };

    /**
     * Gets all data from a guild
     *
     * @param guild_id - The user id Example 1232132132131231
     *
     */

    getAll = async (guild_id: string): Promise<BadWordData[] | false> => {
        try {
            const result = await postgres.query(
                'SELECT * FROM ploxy_badwords WHERE guild_id = $1',
                [guild_id]
            );
            return result.rows;
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };

    deleteAll = async (guild_id: string): Promise<BadWordData[] | false> => {
        try {
            const result = await postgres.query(
                'DELETE FROM ploxy_badwords WHERE guild_id = $1',
                [guild_id]
            );
            return result.rows;
        } catch (error: any) {
            log.error(error);

            return false;
        }
    }
    
}



module.exports = {
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
    BadWords
};

export default BadWords;