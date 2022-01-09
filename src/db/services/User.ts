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
  const res = await getUser(user_id);
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

export const getUser = async (
    user_id?: string,
    username?: string,
    discriminator?: string,
    email?: string
  ) => {
    let query = "SELECT * FROM ploxy_users WHERE ";
    let values = [];
    if (user_id) {
      query += "user_id = $1";
      values.push(user_id);
    }
    if ((username && discriminator) && !user_id) {
      query += "username = $2 && discriminator = $3";
      values.push(username, discriminator);
    }
    if (email && !(user_id && username && discriminator)) {
      query += "email = $4";
      values.push(email);
    }
    if (values.length === 0) {
      log.debug("getUser failed, no values in function to search for");
      return false;
    }

    const res = await postgres.query(query, values);
    if (res.rows.length > 0) {
      return res.rows[0];
    }
    log.debug(`User ${user_id} not found, getUser failed`);
    return false;
}