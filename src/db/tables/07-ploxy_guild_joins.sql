create table if not exists ploxy_guild_joins
(
    id varchar unique not null,
    user_guild_id varchar not null
        constraint ploxy_guild_joins_pk
            primary key
        constraint ploxy_guild_joins_ploxy_guild_members_id_fk
            references ploxy_guild_members,
    guild_id      varchar
        constraint ploxy_guild_joins_ploxy_guilds_guild_id_fk
            references ploxy_guilds,
    user_id      varchar
        constraint ploxy_guild_joins_ploxy_users_user_id_fk
            references ploxy_users,
    invite_link   varchar,
    left_at        timestamptz,
    created_at        timestamptz default NOW() not null,
    updated_at        timestamptz default NOW() not null
);

CREATE EXTENSION IF NOT EXISTS moddatetime;
CREATE TRIGGER update_timestamp BEFORE UPDATE ON ploxy_links
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);
