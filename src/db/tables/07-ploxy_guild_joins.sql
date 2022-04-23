create table if not exists ploxy_guild_joins
(
    id varchar unique not null,
    user_id      varchar,
    invite_link   varchar,
    left_at        timestamptz,
    created_at        timestamptz default NOW() not null,
    updated_at        timestamptz default NOW() not null
);

CREATE EXTENSION IF NOT EXISTS moddatetime;
CREATE TRIGGER update_timestamp BEFORE UPDATE ON ploxy_links
FOR EACH ROW EXECUTE PROCEDURE moddatetime(updated_at);
