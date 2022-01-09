create table if not exists ploxy_automod
(
    guild_id                  varchar              not null
        constraint ploxy_automod_pk
            primary key
        constraint ploxy_automod_ploxy_guilds_guild_id_fk
            references ploxy_guilds,
    bad_word_check            bool   default false not null,
    user_date_check           bool   default false not null,
    minimum_user_age          bigint default 0     not null,
    bad_word_limit            int    default 0     not null,
    message_spam_check        bool   default false not null,
    message_pasta_check       bool   default false not null,
    on_fail_bad_word          int    default 1,
    tempban_time              bigint default 0     not null,
    tempban_time_increment    bigint default 0     not null,
    max_warns_before_kick     int    default 0     not null,
    max_warns_before_temp_ban int    default 0     not null,
    max_warns_before_perm_ban int    default 0,
    mute_time                 bigint default 0     not null,
    mute_time_increment       bigint default 0     not null,
    warn_reset_time           bigint default 0,
    on_fail_spam              int    default 1     not null,
    duplicated_message_check  bool   default false not null,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW()
);

comment on column ploxy_automod.minimum_user_age is '0 for no minimum,
time in minutes for minimum,
10 for 10 minutes,
60 for 1 hour,
1440 for 1 day,
10080 for 7 days
if it fails this then the user is kicked';

comment on column ploxy_automod.bad_word_limit is 'Amount of bad words that can be said in a sentence before moderation happens';

comment on column ploxy_automod.message_spam_check is 'Whether to check if a message is spam or not';

comment on column ploxy_automod.message_pasta_check is 'Check if a message is a pasta or not';

comment on column ploxy_automod.on_fail_bad_word is 'What to do when a bad word is detected and it goes over the limit
0 - Nothing
1 - Warn
2 - Kick
3 - Temp ban - (variable time)
4 - Perm ban';

comment on column ploxy_automod.tempban_time is 'Time to temp ban person';

comment on column ploxy_automod.tempban_time_increment is '-1 Disabled
0 - No effect
1+ - milliseconds to ban for every temp ban they have';

comment on column ploxy_automod.max_warns_before_kick is '0 - Disabled
1+ - How many warns before someone is kicked';

comment on column ploxy_automod.max_warns_before_temp_ban is '0 - disabled
1+ max warns before a temp ban - follows temp ban system';

comment on column ploxy_automod.max_warns_before_perm_ban is '0 - disabled
1+ - amount of warns before perm ban';

comment on column ploxy_automod.max_warns_before_kick is '0 - disabled
1+ - amount of warns until mute';

comment on column ploxy_automod.mute_time is '0 - disabled
1+ amount of time in minutes to mute';

comment on column ploxy_automod.mute_time_increment is 'same as temp ban time, 0 - disabled, each mute increases the mute time for a user';

comment on column ploxy_automod.warn_reset_time is 'Amount of time till warnings get erased from current moderation statistics - still visible but not for any usage other than archive';

comment on column ploxy_automod.on_fail_spam is 'What to do when a spam or a pasta is detected and it goes over the limit
0 - Nothing
1 - Warn
2 - Kick
3 - Temp ban - (variable time)
4 - Perm ban';

create unique index ploxy_automod_guild_id_uindex
    on ploxy_automod (guild_id);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON ploxy_automod
FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();