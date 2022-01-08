create table ploxy_guilds
(
    guild_id                 varchar                not null
        constraint ploxy_guilds_pk
            primary key,
    name                     text                   not null,
    avatar                   text,
    owner_id                 varchar                not null
        constraint ploxy_guilds_ploxy_users_user_id_fk
            references ploxy_users,
    premium                  smallint default 0     not null,
    banned                   smallint default 0     not null,
    payment_level            int      default 0     not null,
    listing                  bool     default false not null,
    has_setup                bool     default false,
    support_packages_enabled bool     default false not null,
    auto_support_enabled     bool     default false not null,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW()
);

comment on column ploxy_guilds.premium is 'Is the guild boosted';

comment on column ploxy_guilds.payment_level is 'In the event it starts accepting premium servers

0 - Not premium
1 - Level 1 premium
2 - Level 2 premium and so on';

comment on column ploxy_guilds.listing is 'False - Private listing for only server members to view
True - Public listing';

comment on column ploxy_guilds.has_setup is 'Has done the web setup for their server';

comment on column ploxy_guilds.support_packages_enabled is '0 - No support packages - /book, /timings etc

1 - Support enabled';

comment on column ploxy_guilds.auto_support_enabled is 'False - No auto support
True - Auto support allowed';

create unique index ploxy_guilds_guild_id_uindex
    on ploxy_guilds (guild_id);

create index ploxy_guilds_listing_index
    on ploxy_guilds (listing);

create index ploxy_guilds_owner_id_index
    on ploxy_guilds (owner_id);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON ploxy_guilds
FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();