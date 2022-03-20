create table if not exists ploxy_guild_members
(
    id             varchar
        constraint ploxy_guild_members_pk
            primary key,
    user_id        varchar not null,
    guild_id       varchar not null,
    roles         text,
    nickname text,
    avatar text,
    muted boolean default false,
    verified       bool default false,
    created_at        timestamptz default NOW() not null,
    updated_at        timestamptz default NOW() not null
);

create unique index ploxy_guild_members_id_uindex
    on ploxy_guild_members (id);


CREATE EXTENSION IF NOT EXISTS moddatetime;
CREATE TRIGGER update_timestamp BEFORE UPDATE ON ploxy_links
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);
