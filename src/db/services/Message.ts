import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';

let redis: RedisClientType;

interface MessageData {
    message_id: string;
    user_id: string
    message: string,
    embed: string,
    channel_id: string,
    guild_id: string,
    in_thread: boolean,
    message_id_before: string,
    created_at: string,
    updated_at: string,
}
class Message {
    constructor(){
        
    }
    createMessage = async (
        message_id: string,
        user_id: string,
        message: string,
        embed: string,
        channel_id: string,
        guild_id: string,
        in_thread: boolean,
        message_id_before: string = '0'
    ): Promise<MessageData | false> => {
        const query = `INSERT INTO ploxy_messages 
    (message_id, user_id, message, embed, channel_id, guild_id, in_thread, message_id_before) 
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`;

        const redisMessageBefore = await redis.get(
            `guild:${guild_id}:last_message`
        );

        if (redisMessageBefore) {
            message_id_before = redisMessageBefore;
        }

        const values = [
            message_id,
            user_id,
            message,
            embed,
            channel_id,
            guild_id,
            in_thread,
            message_id_before,
        ];

        try {
            const result = await postgres.query(query, values);

            await redis.set(`guild:${guild_id}:last_message`, message_id);

            return result.rows.at(0) as MessageData;
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };

    getMessage = async (message_id: string): Promise<MessageData | false> => {
        const query = 'SELECT * FROM ploxy_messages WHERE message_id = $1';
        const values = [message_id];

        try {
            const result = await postgres.query(query, values);

            return result.rows.at(0) as MessageData;
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };

    getMessagesFromGuild = async (guild_id: string): Promise<MessageData[] | false> => {
        const query = 'SELECT * FROM ploxy_messages WHERE guild_id = $1';
        const values = [guild_id];

        try {
            const result = await postgres.query(query, values);

            return result.rows as MessageData[];
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };

    getMessagesFromUser = async (user_id: string): Promise<MessageData[] | false> => {
        const query = 'SELECT * FROM ploxy_messages WHERE user_id = $1';
        const values = [user_id];

        try {
            const result = await postgres.query(query, values);

            return result.rows as MessageData[];
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };

}

export const setRedis = function (redisIn: RedisClientType) {redis = redisIn};

export default new Message();