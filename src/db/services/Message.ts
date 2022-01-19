import postgres from '../postgres';
import log from '../../utils/log';
import { RedisClientType } from 'redis';

let redis: RedisClientType;

const createMessage = async (
  message_id: string,
  user_id: string,
  message: string,
  embed: string,
  channel_id: string,
  guild_id: string,
  in_thread: string,
  message_id_before: string = "0",
) => {
  const query = `INSERT INTO ploxy_messages 
  (message_id, user_id, message, embed, channel_id, guild_id, in_thread, message_id_before) 
  VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`
  
  const redisMessageBefore = await redis.get(`guild:${guild_id}:last_message`);

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
    message_id_before
  ]

  try {
    const res = await postgres.query(query, values);

    await redis.set(`guild:${guild_id}:last_message`, message_id);

    return res.rows[0]
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
