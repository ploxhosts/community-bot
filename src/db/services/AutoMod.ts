/* eslint-disable unicorn/prevent-abbreviations */
import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';

let redis: RedisClientType;

class AutoMod {
    addGuildAutoMod = async (
        guild_id: string,
        bad_word_check: boolean,
        user_date_check: boolean,
        minimum_user_age: number,
        bad_word_limit: number,
        message_spam_check: boolean,
        message_pasta_check: boolean,
        on_fail_bad_word: boolean,
        tempban_time: number,
        tempban_time_increment: number,
        max_warns_before_kick: number,
        max_warns_before_temporary_ban: number,
        max_warns_before_perm_ban: number,
        mute_time: number,
        mute_time_increment: number,
        warn_reset_time: number,
        on_fail_spam: number,
        duplicated_message_check: boolean
    ) => {
        try {
            const res = await postgres.query(
                `INSERT INTO ploxy_automod (
            guild_id, bad_word_check, user_date_check, 
            minimum_user_age, bad_word_limit, 
            message_spam_check, message_pasta_check, 
            on_fail_bad_word, tempban_time, tempban_time_increment, 
            max_warns_before_kick, max_warns_before_temp_ban, 
            max_warns_before_perm_ban, mute_time, 
            mute_time_increment, warn_reset_time, 
            on_fail_spam, duplicated_message_check) VALUES ($1, $2, $3, $4, $5. $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)`,
                [
                    guild_id,
                    bad_word_check,
                    user_date_check,
                    minimum_user_age,
                    bad_word_limit,
                    message_spam_check,
                    message_pasta_check,
                    on_fail_bad_word,
                    tempban_time,
                    tempban_time_increment,
                    max_warns_before_kick,
                    max_warns_before_temporary_ban,
                    max_warns_before_perm_ban,
                    mute_time,
                    mute_time_increment,
                    warn_reset_time,
                    on_fail_spam,
                    duplicated_message_check,
                ]
            );
    
            await redis.set(`automod:${guild_id}`, JSON.stringify(res.rows.at(0)));
    
            return res.rows.at(0);
        } catch (error: any) {
            log.error(error);
    
            return false;
        }
    };

    getGuildAutoMod = async (guild_id: string) => {
        try {
            const res = await redis.get(`automod:${guild_id}`);
    
            if (res) {
                return JSON.parse(res);
            }
    
            const data = await postgres.query(
                'SELECT * FROM ploxy_automod WHERE guild_id = $1',
                [guild_id]
            );
    
            if (!data.rows.at(0)) {
                // Data does not exist
                return false;
            }
    
            await redis.set(`automod:${guild_id}`, JSON.stringify(data.rows.at(0)));
    
            return data.rows.at(0);
        } catch (error: any) {
            log.error(error);
    
            return false;
        }
    };

    updateGuildAutoMod = async (
        guild_id: string,
        bad_word_check: boolean,
        user_date_check: boolean,
        minimum_user_age: number,
        bad_word_limit: number,
        message_spam_check: boolean,
        message_pasta_check: boolean,
        on_fail_bad_word: boolean,
        tempban_time: number,
        tempban_time_increment: number,
        max_warns_before_kick: number,
        max_warns_before_temporary_ban: number,
        max_warns_before_perm_ban: number,
        mute_time: number,
        mute_time_increment: number,
        warn_reset_time: number,
        on_fail_spam: number,
        duplicated_message_check: boolean
    ) => {
        try {
            const res = await postgres.query(
                `UPDATE ploxy_automod SET
            bad_word_check = $1, user_date_check = $2, 
            minimum_user_age = $3, bad_word_limit = $4, 
            message_spam_check = $5, message_pasta_check = $6, 
            on_fail_bad_word = $7, tempban_time = $8, tempban_time_increment = $9, 
            max_warns_before_kick = $10, max_warns_before_temp_ban = $11, 
            max_warns_before_perm_ban = $12, mute_time = $13, 
            mute_time_increment = $14, warn_reset_time = $15, 
            on_fail_spam = $16, duplicated_message_check = $17 WHERE guild_id = $18`,
                [
                    bad_word_check,
                    user_date_check,
                    minimum_user_age,
                    bad_word_limit,
                    message_spam_check,
                    message_pasta_check,
                    on_fail_bad_word,
                    tempban_time,
                    tempban_time_increment,
                    max_warns_before_kick,
                    max_warns_before_temporary_ban,
                    max_warns_before_perm_ban,
                    mute_time,
                    mute_time_increment,
                    warn_reset_time,
                    on_fail_spam,
                    duplicated_message_check,
                    guild_id,
                ]
            );
    
            await redis.set(`automod:${guild_id}`, JSON.stringify(res.rows.at(0)));
    
            return res.rows.at(0);
        } catch (error: any) {
            log.error(error);
    
            return false;
        }
    };

    deleteGuildAutoMod = async (guild_id: string) => {
        try {
            await postgres.query('DELETE FROM ploxy_automod WHERE guild_id = $1', [
                guild_id,
            ]);
    
            return await redis.del(`automod:${guild_id}`);
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
    AutoMod
};

export default AutoMod;
