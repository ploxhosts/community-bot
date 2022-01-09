import postgres from '../postgres';
import log from '../../utils/log';

export const createUser = async (
    user_id: string,
    username: string,
    discriminator: string,
    user_avatar: string | null = null,
    email: string | null = null,
    premium : number,
    banned: number = 0
  ) => {
  const res = await postgres.query("SELECT * FROM ploxy_users WHERE user_id = ?", [user_id]);
  if (res.rows.length > 0) {
    log.debug(`User ${user_id} already exists, createUser failed`);
    return res.rows.length;
  }
  let result;
  try {
    result = await postgres.query(
      "INSERT INTO ploxy_users (user_id, username, discriminator, user_avatar, email, premium, banned) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *",
      [user_id, username, discriminator, user_avatar, email, premium, banned])
  } catch (err: any) {
    log.error(err);
    return false;
  }
  
  return result.rows[0];
}