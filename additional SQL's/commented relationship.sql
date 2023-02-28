use photoshare;

create table commented(
	user_id int not null,
    comment_id int unique,
    primary key(user_id, commented_id),
    foreign key(user_id) references users(user_id),
    foreign key(comment_id) references comments(comment_id)
);

