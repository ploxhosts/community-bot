create table if not exists ploxy_users
(
    user_id       varchar not null
        constraint ploxy_users_pk
            primary key,
    username      text    not null,
    discriminator varchar not null,
    user_avatar   TEXT,
    email         text,
    premium       smallint default 0,
    banned        int      default 0,
    roles         text,
    ip           text,
    nickname text,
    muted boolean default false,
    verified       bool default false,
    banned       bool default false,
    banned_until  timestamptz,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW()
);

create index ploxy_users_email_index
    on ploxy_users (email);

create unique index ploxy_users_user_id_uindex
    on ploxy_users (user_id);
    
CREATE EXTENSION IF NOT EXISTS moddatetime;
CREATE TRIGGER update_timestamp BEFORE UPDATE ON ploxy_users
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);