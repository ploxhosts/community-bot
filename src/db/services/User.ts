import postgres from '../postgres';

export const createUser = async (user_id: string) => {
  
  const res = await postgres.query("SELECT * FROM ploxy_users WHERE user_id = ?", [user_id]);
}