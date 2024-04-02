/******************************\
 *  INITIALIZE
\******************************/ 

drop database IF EXISTS $database;
create database $database;
use $database;

/******************************\
 * TABLES
\******************************/ 

/***** APP *****/

create table digiQuest(
    version varchar(20) primary key not null
);

/***** USER *****/

create table user(
    id varchar(36) primary key not null,
    username varchar(1000) COLLATE latin1_general_cs not null,
    mdp varchar(1000) COLLATE latin1_general_cs not null,
    token varchar(36) unique,
    expiration_date datetime
);

create table accountPrivilege(
    id varchar(36) primary key not null,
    label varchar(256) not null unique,
    roles varchar(256) not null,
    editable bool not null default 1
);

create table userAccount(
    id varchar(36) primary key not null,
    idU varchar(36) not null,
    idP varchar(36) not null,
    is_authenticated bool not null default 0,
    is_active bool not null default 0,
    is_disabled bool not null default 0,
    language varchar(256) not null default "fr",
    foreign key (idU) references user(id),
    foreign key (idP) references accountPrivilege(id)
);

CREATE TABLE userGCalendar (
    user varchar(36) primary key not null,
    calendar varchar(200) not null,
    sync bool not null default 1,
    foreign key (user) references user(id)
);

/***** QUESTS *****/

create table quest(
    id varchar(36) primary key not null,
    owner varchar(36) not null,
    title varchar(100) not null,
    description varchar(500),
    complete bool not null default 0,
    archived bool not null default 0,
    reccurence int not null default 0,
    reccurence_config varchar(250),
    foreign key (owner) references user(id)
);

create table task(
    id varchar(36) primary key not null,
    quest varchar(36) not null,
    content varchar(200) not null,
    task_order int not null default 0,
    complete bool not null default 0,
    foreign key (quest) references quest(id)
);

create table taskMonitor(
    id varchar(36) primary key not null,
    task varchar(36) not null,
    type varchar(100) not null,
    params varchar(2000),
    foreign key (task) references task(quest)
);

create table activeQuest(
    user varchar(36) primary key not null,
    quest varchar(36) not null,
    foreign key (quest) references quest(id),
    foreign key (user) references user(id)
);


/***** EVENTS *****/

create table event(
    id varchar(36) primary key not null,
    quest varchar(36),
    task varchar(36),
    start_date datetime not null,
    end_date datetime not null,
    synced bool not null default 0,
    constraint unique_event unique (task),
    foreign key (quest) references quest(id),
    foreign key (task) references task(id)
);

create table gevent(
    event varchar(36) primary key not null,
    owner varchar(36) not null,
    gcalendar_id varchar(200) not null,
    gevent_id varchar(200) not null,
    foreign key (event) references event(id),
    foreign key (owner) references user(id)
);

/***** RESOURCE *****/

create table resourceKey(
    id varchar(36) primary key not null,
    resource varchar(36) not null,
    resource_type varchar(150) not null,
    user varchar(36),
    resource_key varchar(250) not null,
    constraint unique_key unique (resource, user),
    foreign key (user) references user(id)
);

/***** JOBS *****/

create table job(
    name varchar(50) primary key not null,
    state varchar(20) not null default "IDLE",
    last_exit_code int
);