import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';

let redis: RedisClientType;

class Links {
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
    addLink = async (
        hostname: string,
        link: string,
        addedBy: string | undefined,
        score: number,
        process: { type: string; score: number }[],
        guildId: string | undefined,
        allowed: boolean
    ) => {
        try {
            const databaseCheck = await this.checkLinkInDB(link, hostname, guildId);

            if (
                databaseCheck &&
                databaseCheck.score < score &&
                databaseCheck.allowed
            ) { // if it exists, if the stored score is lower than the new score and it's currently allowed
                await this.removeLink(link, hostname, guildId);
                console.log('removed from link db', link, hostname, guildId);
            } else if (databaseCheck && databaseCheck.score >= score) {
                return;
            } else if (databaseCheck) {
                return;
            }
            
            const hostnameCheck = await this.checkExistanceByHostname(hostname, guildId);

            if (hostnameCheck) {
                return;
            }

            const result = await postgres.query(
                'INSERT INTO ploxy_links (hostname, added_by, score, process, guild_id, allowed, link) VALUES ($1, $2, $3, $4, $5, $6, $7)',
                [
                    hostname,
                    addedBy,
                    score,
                    JSON.stringify(process),
                    guildId,
                    allowed,
                    link,
                ]
            );

            await redis.set(
                `link:${hostname}:${guildId}`,
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

    removeLink = async (
        hostname: string,
        link: string,
        guildId: string | undefined
    ) => {
        try {
            await (guildId
                ? postgres.query(
                    'DELETE FROM ploxy_links WHERE (link = $1 OR hostname = $2) AND guild_id = $3',
                    [link, hostname, guildId]
                )
                : postgres.query(
                    'DELETE FROM ploxy_links WHERE (link = $1 OR hostname = $2) AND guild_id is NULL',
                    [link, hostname]
                ));

            return await redis.del(`link:${hostname}:${guildId}`);
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };

    /**
     * Check existance by hostname
     *
     */

    checkExistanceByHostname = async (
        hostname: string,
        guildId: string | undefined
    ): Promise<any> => {
        try {
            const redisResult = await redis.get(`link:${hostname}:${guildId}`);

            if (redisResult) {
                return JSON.parse(redisResult);
            }

            const result = await (guildId
                ? postgres.query(
                    'SELECT * FROM ploxy_links WHERE hostname = $1 AND guild_id = $2',
                    [hostname, guildId]
                )
                : postgres.query(
                    'SELECT * FROM ploxy_links WHERE hostname = $1 AND guild_id is NULL',
                    [hostname]
                ));

            return result.rowCount > 0 ? result.rows.at(0) : undefined;
        } catch (error: any) {
            log.error(error);

            return undefined;
        }
    };

    /**
     * Check a link
     *
     */

    checkLinkInDB = async (
        link: string,
        hostname: string,
        guildId: string | undefined
    ): Promise<any> => {
        try {
            const redisResult = await redis.get(`link:${hostname}:${guildId}`);

            if (redisResult) {
                return JSON.parse(redisResult);
            }

            const result = await (guildId
                ? postgres.query(
                    'SELECT * FROM ploxy_links WHERE (link = $1 OR hostname = $2) AND guild_id = $3',
                    [link, hostname, guildId]
                )
                : postgres.query(
                    'SELECT * FROM ploxy_links WHERE (link = $1 OR hostname = $2) AND guild_id is NULL',
                    [link, hostname]
                ));

            return result.rowCount > 0 ? result.rows.at(0) : undefined;
        } catch (error: any) {
            log.error(error);

            return undefined;
        }
    };

    /**
     * Gets all links
     *
     */

    getAllLinks = async () => {
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

    getAllLinksByGuildId = async (guildId: string) => {
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
}
module.exports = {
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
    Links
};

export default Links;
