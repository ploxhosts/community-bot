create table if not exists ploxy_messages
(
    message_id        varchar                   not null
        constraint ploxy_messages_pk
            primary key,
    user_id           varchar                   not null,
    message           text        default null,
    embed             text        default null,
    channel_id        varchar                   not null,
    guild_id          varchar                   not null,
    in_thread         bool        default false not null,
    message_id_before varchar                   not null,
    created_at        timestamptz default NOW() not null,
    updated_at        timestamptz default NOW() not null
);

create unique index ploxy_messages_message_id_uindex
    on ploxy_messages (message_id);

create index ploxy_messages_user_id_index
    on ploxy_messages (user_id);

CREATE EXTENSION IF NOT EXISTS moddatetime;
CREATE TRIGGER update_timestamp BEFORE UPDATE ON ploxy_messages
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);