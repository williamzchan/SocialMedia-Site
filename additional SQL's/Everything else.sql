use photoshare;

create table owner(
	user_id int not null,
    album_id int unique,
    primary key(user_id, album_id),
    foreign key(user_id) references users(user_id),
    foreign key(album_id) references album(album_id)
);

create table AhasP(
	album_id int not null,
    picture_id int unique,
    primary key (album_id, photo_id),
    foreign key (album_id) references album(album_id),
    foreign key (picture_id) references pictures(picture_id)
);

create table tagged(
	tag_name char(6),
    picture_id int,
    primary key (tag_name, picture_id),
    foreign key (tag_name) references tag(tag_name),
    foreign key (picture_id) references pictures(picture_id)
);

alter table `social_media`.`album`
change column `user_id` `user_id` int not null,
add foreign key (user_id) references owner(user_id);

alter table `social_media`.`pictures`
change column `user_id` `user_id` int not null,
add foreign key (user_id) references owner(user_id);