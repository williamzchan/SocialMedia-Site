use photoshare;

create table likes(
	user_id int not null,
    picture_id int,
    primary key(user_id, picture_id),
    foreign key(user_id) references users(user_id),
    foreign key(picture_id) references pictures(picture_id)
)