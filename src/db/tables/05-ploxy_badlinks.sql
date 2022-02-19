create table if not exists ploxy_badlinks
(
    id       bigserial
        constraint ploxy_badlinks_pk
            primary key,
    link     text not null,
    added_by varchar
        constraint ploxy_badlinks_ploxy_users_user_id_fk
            references ploxy_users,
    created_at        timestamptz default NOW() not null,
    updated_at        timestamptz default NOW() not null
);

create unique index ploxy_badlinks_id_uindex
    on ploxy_badlinks (id);


CREATE EXTENSION IF NOT EXISTS moddatetime;
CREATE TRIGGER update_timestamp BEFORE UPDATE ON ploxy_badlinks
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);
