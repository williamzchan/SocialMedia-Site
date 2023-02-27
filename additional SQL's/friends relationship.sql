create table friends(
	user1_ID int,
	 user2_ID int,
	 primary Key (user1_ID, user2_ID),
	 foreign key (user1_ID) references users(user_ID),
	 foreign key (user2_ID) references users(user_ID)
 )	