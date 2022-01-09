import postgres from '../postgres';
import log from '../../utils/log';

/**
 * Creates a new user
 *
 * @param user_id - The user id Example 123213021032131
 * @param username - The username Example JohnJames
 * @param discriminator - The discriminator/tag of the user without the hashtag # Example 1234
 * @param user_avatar - Profile image url of the user, link to the cdn
 * @param email - The user email address Example JohnJames@example.com
 * @param premium - The nitro level of the user - Going to be 0 if no nitro
 * @param banned - If the user is banned from using the bot as in rate limit - Going to be 0 if not fulfilled
 *
 */
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

export const updateUser = async (
    user_id: string,
    username: string,
    discriminator: string,
    user_avatar: string | null = null,
    email: string | null = null,
    premium : number,
    banned: number = 0
  ) => {
  const res = await getUser(user_id);
  if (res.rows.length === 0) {
    log.debug(`User ${user_id} not found, updateUser failed`);
    return false;
  }
  let result;
  try {
    result = await postgres.query(
      "UPDATE ploxy_users SET username = $1, discriminator = $2, user_avatar = $3, email = $4, premium = $5, banned = $6 WHERE user_id = $7 RETURNING *",
      [username, discriminator, user_avatar, email, premium, banned, user_id])
  } catch (err: any) {
    log.error(err);
    return false;
  }
  
  return result.rows[0];
}