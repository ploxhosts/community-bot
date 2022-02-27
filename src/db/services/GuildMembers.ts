import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';
import { nanoid } from 'nanoid';

let redis: RedisClientType;

interface GuildMemberData {
    id: string,
    guild_id: string,
    user_id: string,
    nickname: string,
    created_at: string,
    updated_at: string,
    verified: boolean,
    muted: boolean,
    avatar: string,
    roles: string
}

class GuildMember {
    constructor(){
        
    }
    /**
     * @param {string} guild_id - The guild id
     * @param {string} user_id - The user id
     * @param {boolean} verified - Used if server entry protection is enabled
     * @param {string[]}  roles - The roles
     * @param {string}  nickname - The nickname
     * @param {string}  avatar - The avatar
     * @param {boolean} muted - If they are muted or not
     * @description Creates a guild
     **/

    createGuildMember = async (
        guild_id: string,
        user_id: string,
        verified: boolean,
        roles: string[],
        nickname: string,
        avatar: string,
        muted: boolean,
    ): Promise<GuildMemberData | boolean> => {
        const id = nanoid();

        const query = `INSERT INTO ploxy_guild_members (
            id,
            user_id,
            guild_id,
            roles,
            verified,
            nickname,
            avatar,
            muted
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`;
        const values = [
            id,
            user_id,
            guild_id,
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

    getGuildMember = async (guild_id: string, user_id: string): Promise<GuildMemberData | false> => {
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

    getGuildsMembers = async (guild_id: string): Promise<GuildMemberData[] | boolean> => {
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
     * @param {boolean} verified - Used if server entry protection is enabled
     * @param {string[]}  roles - The roles
     * @param {string}  nickname - The nickname
     * @param {string}  avatar - The avatar
     * @param {boolean} muted - If they are muted or not
     * @description Updates a guild member
     **/

    updateGuildMember = async (
        guild_id: string,
        user_id: string,
        verified?: boolean,
        roles?: string[],
        nickname?: string,
        avatar?: string,
        muted?: boolean,
    ): Promise<GuildMemberData | boolean> => {

        const update: any = {};

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

    deleteGuildMember = async (guild_id: string, user_id: string): Promise<GuildMemberData | false> => {
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

    /**
     * @param {string} guild_id - The guild id
     * 
     * @description Deletes all Guild Members
     */
    deleteGuildMembers = async (guild_id: string): Promise<GuildMemberData[] | false> => {
        const query = 'DELETE FROM ploxy_guild_members WHERE guild_id = $1';
        const values = [guild_id];

        try {
            const result = await postgres.query(query, values);

            return result.rows;
        } catch (error) {
            return false;
        }
    };
    
    memberJoin = async (
        guild_id: string,
        user_id: string,
        invite_link: string,
    ): Promise<GuildMemberData | false> => {
        const member = await this.getGuildMember(guild_id, user_id);
        if (member == false){ // If the member doesn't exist, prevents errors from bad code
            return false;
        }
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

    memberLeave = async (guild_id: string, user_id: string): Promise<GuildMemberData | false> => {
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

}
export const setRedis = function (redisIn: RedisClientType) {redis = redisIn};

export default new GuildMember();