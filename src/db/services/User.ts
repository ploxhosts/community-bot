import { RedisClientType } from 'redis';

import log from '../../utils/log';
import postgres from '../postgres';

let redis: RedisClientType;

interface UserData {
    user_id: string;
    username: string;
    discriminator: string;
    user_avatar: string;
    email: string | undefined;
    premium: number,
    banned: number,
    created_at: string,
    updated_at: string,
}

class User {
    constructor(){
        
    }
    /**
     * Creates a new user
     *
     * @param user_id - The user id Example 123213021032131
     * @param username - The username Example JohnJames
     * @param discriminator - The discriminator/tag of the user without the # Example 1234
     * @param user_avatar - Profile image url of the user, link to the cdn
     * @param email - The user email address Example JohnJames@example.com
     * @param premium - The nitro level of the user - Going to be 0 if no nitro
     * @param banned - If the user is banned from using the bot as in rate limit - Going to be 0 if not fulfilled
     *
     */
    createUser = async (
        user_id: string,
        username: string,
        discriminator: string,
        user_avatar: string | undefined,
        email: string | undefined,
        premium: number,
        banned: number = 0
    ): Promise<UserData | Boolean> => {
        const response = await this.getUser(user_id);

        if (response) {
            log.debug(`User ${user_id} already exists, createUser failed`);

            return response;
        }

        let result;

        try {
            result = await postgres.query(
                'INSERT INTO ploxy_users (user_id, username, discriminator, user_avatar, email, premium, banned) VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *',
                [
                    user_id,
                    username,
                    discriminator,
                    user_avatar,
                    email,
                    premium,
                    banned,
                ]
            );

            await redis.set(`user:${user_id}`, JSON.stringify(result.rows.at(0)));

            return result.rows.at(0) as UserData;
        } catch (error: any) {
            log.error(error);

            return false;
        }
    };

    /**
     * Fetches a user from the database, user_id or email should be provided. If supplying both username or discriminator, provide both username and discriminator to function.
     *
     * @param user_id - The user id Example 123213021032131
     * @param username - The username, must also be supplpied with a discriminator Example JohnJames
     * @param discriminator - The discriminator/tag of the user without the # Example 1234
     * @param email - The user email address Example JohnJames@example.com
     *
     */
    getUser = async (
        user_id?: string,
        username?: string,
        discriminator?: string,
        email?: string
    ): Promise<UserData | boolean> => {
        let query = 'SELECT * FROM ploxy_users WHERE ';
        const values = [];

        if (user_id) {
            query += 'user_id = $1';
            values.push(user_id);
        }

        if (username && discriminator && !user_id) {
            query += 'username = $2 && discriminator = $3';
            values.push(username, discriminator);
        }

        if (email && !(user_id && username && discriminator)) {
            query += 'email = $4';
            values.push(email);
        }

        if (values.length === 0) {
            log.debug('getUser failed, no values in function to search for');

            return false;
        }

        try {
            const userCache = await redis.get(`user:${user_id}`);

            if (userCache) {
                return JSON.parse(userCache);
            }

            const result = await postgres.query(query, values);

            if (result.rows.length > 0) {
                return result.rows.at(0);
            }

            log.debug(`User ${user_id} not found, getUser failed`);
        } catch (error: any) {
            log.error(error);
        }

        return false;
    };

    /**
     * Updates a user in the database, supply all data and change what is wanted.
     *
     * @param user_id - The user id Example 123213021032131
     * @param username - The username Example JohnJames
     * @param discriminator - The discriminator/tag of the user without the # Example 1234
     * @param user_avatar - Profile image url of the user, link to the cdn
     * @param email - The user email address Example JohnJames@example.com
     * @param premium - The nitro level of the user - Going to be 0 if no nitro
     * @param banned - If the user is banned from using the bot as in rate limit - Going to be 0 if not fulfilled
     *
     */
    updateUser = async (
        user_id: string,
        username: string,
        discriminator: string,
        user_avatar: string | undefined,
        email: string | undefined,
        premium: number,
        banned: number = 0
    ): Promise<UserData | boolean> => {
        const UserResult = await this.getUser(user_id);

        if (!UserResult) {
            log.debug(`User ${user_id} not found, updateUser failed`);

            return false;
        }

        let result;

        try {
            result = await postgres.query(
                'UPDATE ploxy_users SET username = $1, discriminator = $2, user_avatar = $3, email = $4, premium = $5, banned = $6 WHERE user_id = $7 RETURNING *',
                [
                    username,
                    discriminator,
                    user_avatar,
                    email,
                    premium,
                    banned,
                    user_id,
                ]
            );
            await redis.set(`user:${user_id}`, JSON.stringify(result.rows.at(0)));

            return result.rows.at(0) as UserData;
        } catch (error: any) {
            log.error(error);

            return false;
        }

        return result.rows.at(0);
    };

    deleteUser = async (user_id: string) => {
        await redis.del(`user:${user_id}`);

        return postgres.query('DELETE FROM ploxy_users WHERE user_id = $1', [
            user_id,
        ]);
    };
}
export const setRedis = function (redisIn: RedisClientType) {redis = redisIn};
export default new User();