create table if not exists ploxy_badwords
(
    word_id    serial,
    guild_id   varchar        not null,
    word       text           not null,
    implicit   bool default false not null,
    created_by varchar        not null
        constraint ploxy_badwords_ploxy_users_user_id_fk
            references ploxy_users,
    created_at timestamptz NOT NULL DEFAULT NOW(),
    updated_at timestamptz NOT NULL DEFAULT NOW()
);

comment on column ploxy_badwords.word is 'The word that is to be blocked';

comment on column ploxy_badwords.implicit is 'Overwrite to check to search if the word exists within another word. Mainly here for web use';

create unique index if not exists ploxy_badwords_word_id_uindex
    on ploxy_badwords (word_id);

CREATE EXTENSION IF NOT EXISTS moddatetime;
CREATE TRIGGER update_timestamp BEFORE UPDATE ON ploxy_badwords
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);