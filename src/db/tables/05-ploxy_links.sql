create table if not exists ploxy_links
(
    id       bigserial
        constraint ploxy_links_pk
            primary key,
    hostname     text not null,
    link     text not null,
    added_by varchar
        constraint ploxy_links_ploxy_users_user_id_fk
            references ploxy_users,
    guild_id varchar
        constraint ploxy_links_ploxy_guilds_guild_id_fk
            references ploxy_guilds,
    allowed boolean
        default false
        not null,
    score bigint default 0 not null,
    process text,
    created_at        timestamptz default NOW() not null,
    updated_at        timestamptz default NOW() not null
);

create unique index ploxy_links_id_uindex
    on ploxy_links (id);

create index ploxy_links_link_idx
    on ploxy_links (link);


CREATE EXTENSION IF NOT EXISTS moddatetime;
CREATE TRIGGER update_timestamp BEFORE UPDATE ON ploxy_links
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);
