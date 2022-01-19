create table ploxy_messages
(
    message_id        varchar                   not null
        constraint ploxy_messages_pk
            primary key
        constraint ploxy_messages_ploxy_messages_message_id_fk
            references ploxy_messages,
    user_id           varchar                   not null
        constraint ploxy_messages_ploxy_users_user_id_fk
            references ploxy_users,
    message           text        default null,
    embed             text        default null,
    channel_id        varchar                   not null,
    guild_id          varchar                   not null
        constraint ploxy_messages_ploxy_guilds_guild_id_fk
            references ploxy_guilds,
    in_thread         bool        default false not null,
    message_id_before varchar                   not null,
    created_at        timestamptz default NOW() not null,
    updated_at        timestamptz default NOW() not null
);

create unique index ploxy_messages_message_id_uindex
    on ploxy_messages (message_id);

create index ploxy_messages_user_id_index
    on ploxy_messages (user_id);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON ploxy_badwords
FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();