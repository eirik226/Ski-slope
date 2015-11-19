drop table if exists users;
drop table if exists utleie;

create table users (
	id integer primary key autoincrement,
	username text not null,
	email text not null,
	password text not null
);
create table utleie (
	id integer primary key autoincrement,
	pakke text not null,
	alder integer not null,
	leietid text not null,
	leieantall integer not null
);