-- table name would be the driver's name

id SERIAL NOT NULL PRIMARY KEY,
ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
epoch integer null,
kind varchar(255) null,
doer varchar(255) null,
isPair boolean DEFAULT FALSE,
pairID integer null,
isValid boolean DEFAULT TRUE,
note json null