import postgres from '../postgres';
import log from '../../utils/log';


export const addGuildAutoMod = (
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
  max_warns_before_temp_ban: number,
  max_warns_before_perm_ban: number,
  mute_time: number,
  mute_time_increment: number,
  warn_reset_time: number,
  on_fail_spam: number,
  duplicated_message_check: boolean
) => {
  try {
    return postgres.query(
      `INSERT INTO ploxy_automod (
        guild_id, bad_word_check, user_date_check, 
        minimum_user_age, bad_word_limit, 
        message_spam_check, message_pasta_check, 
        on_fail_bad_word, tempban_time, tempban_time_increment, 
        max_warns_before_kick, max_warns_before_temp_ban, 
        max_warns_before_perm_ban, mute_time, 
        mute_time_increment, warn_reset_time, 
        on_fail_spam, duplicated_message_check) VALUES ($1, $2, $3, $4, $5. $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)`,
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
        max_warns_before_temp_ban,
        max_warns_before_perm_ban,
        mute_time,
        mute_time_increment,
        warn_reset_time,
        on_fail_spam,
        duplicated_message_check
      ]
    );
  } catch (error: any) {
    log.error(error);
    return false;
  }

}


export const getGuildAutoMod = (guild_id: string) => {
  try {
    return postgres.query(
      `SELECT * FROM ploxy_automod WHERE guild_id = $1`,
      [guild_id]
    );
  } catch (error: any) {
    log.error(error);
    return false;
  }
}