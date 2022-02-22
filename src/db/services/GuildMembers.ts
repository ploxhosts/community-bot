import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';
import { nanoid } from 'nanoid';

let redis: RedisClientType;
/**
 * @param {string} guild_id - The guild id
 * @param {string} user_id - The user id
 * @param {string[]} panel_settings - The panel settings
 * @param {boolean} verified - Used if server entry protection is enabled
 * @param {string[]}  roles - The roles
 * @param {string}  nickname - The nickname
 * @param {string}  avatar - The avatar
 * @param {boolean} muted - If they are muted or not
 * @description Creates a guild
 **/

export const createGuildMember = async (
    guild_id: string,
    user_id: string,
    panel_settings: string[],
    verified: boolean,
    roles: string[],
    nickname: string,
    avatar: string,
    muted: boolean,
) => {
    const id = nanoid();

    const query = `INSERT INTO ploxy_guild_members (
        id,
        user_id,
        guild_id,
        panel_settings,
        roles,
        verified,
        nickname,
        avatar,
        muted
  ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)`;
    const values = [
        id,
        user_id,
        guild_id,
        JSON.stringify(panel_settings),
        JSON.stringify(roles),
        verified,
        nickname,
        avatar,
        muted,
    ];

    try {
        const result = await postgres.query(query, values);

        return result.rows.at(0);
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * @param {string} guild_id - The guild id
 * @param {string} user_id - The user id
 * 
 * @description Gets a guild member
 */

export const getGuildMember = async (guild_id: string, user_id: string) => {
    const query = 'SELECT * FROM ploxy_guild_members WHERE guild_id = $1 AND user_id = $2';
    const values = [guild_id, user_id];

    try {
        const result = await postgres.query(query, values);

        return result.rows.at(0);
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 *
 * @description Gets a guilds Members
 */

export const getGuildsMembers = async (guild_id: string) => {
    const query = 'SELECT * FROM ploxy_guilds WHERE guild_id = $1';
    const values = [guild_id];

    try {
        const result = await postgres.query(query, values);

        return result.rows;
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * @param {string} guild_id - The guild id
 * @param {string} user_id - The user id
 * @param {string[]} panel_settings - The panel settings
 * @param {boolean} verified - Used if server entry protection is enabled
 * @param {string[]}  roles - The roles
 * @param {string}  nickname - The nickname
 * @param {string}  avatar - The avatar
 * @param {boolean} muted - If they are muted or not
 * @description Updates a guild member
 **/

export const updateGuildMember = async (
    guild_id: string,
    user_id: string,
    panel_settings?: string[],
    verified?: boolean,
    roles?: string[],
    nickname?: string,
    avatar?: string,
    muted?: boolean,
) => {

    const update: any = {};

    if (panel_settings) {
        update.panel_settings = JSON.stringify(panel_settings);
    }

    if (verified) {
        update.verified = verified;
    }

    if (roles) {
        update.roles = JSON.stringify(roles);
    }

    if (nickname) {
        update.nickname = nickname;
    }

    if (avatar) {
        update.avatar = avatar;
    }

    if (muted) {
        update.muted = muted;
    }

    const query = `UPDATE ploxy_guild_members SET ${Object.keys(update).map(
        (key) => `${key} = $${Object.keys(update).indexOf(key) + 2}`,
    )} WHERE guild_id = $1 AND user_id = $2`;
    const values = [guild_id, user_id, ...Object.values(update)];

    try {
        const result = await postgres.query(query, values);
        return result.rows.at(0);
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

/**
 * @param {string} guild_id - The guild id
 * @param {string} user_id - The user id
 *
 * @description Deletes a Guild Member
 */

export const deleteGuildMember = async (guild_id: string, user_id: string) => {
    const query = 'DELETE FROM ploxy_guilds WHERE guild_id = $1 AND user_id = $2';
    const values = [guild_id, user_id];

    try {
        const result = await postgres.query(query, values);

        return result.rows.at(0);
    } catch (error: any) {
        log.error(error);

        return false;
    }
};

const memberJoin = async (
    guild_id: string,
    user_id: string,
    invite_link: string,
) => {
    const member = await getGuildMember(guild_id, user_id);
    const query = `INSERT INTO ploxy_guild_members (
        id,
        user_guild_id,
        guild_id,
        user_id,
        invite_link ) VALUES ($1, $2, $3, $4, $5)`;
    const values = [
        nanoid(),
        member.id,
        guild_id,
        user_id,
        invite_link,
    ];
    try {
        const result = await postgres.query(query, values);

        return result.rows.at(0);
    } catch (error: any) {
        log.error(error);

        return false;
        
    }
};

const memberLeave = async (guild_id: string, user_id: string) => {
    let query = `UPDATE ploxy_guild_members SET verified = false WHERE guild_id = $1 AND user_id = $2`;
    const values = [guild_id, user_id];

    try {
        const result = await postgres.query(query, values);

        query = `UPDATE ploxy_guild_joins SET left_at = NOW() WHERE guild_id = $1 AND user_id = $2 AND user_guild_id = $3`;
        values.push(result.rows.at(0).id);
        const finalResult = await postgres.query(query, values);

        return finalResult.rows.at(0);
    }
    catch (error: any) {
        log.error(error);

        return false;
    }

};
module.exports = {
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
    createGuildMember,
    deleteGuildMember,
    updateGuildMember,
    getGuildMember,
    getGuildsMembers,
};
