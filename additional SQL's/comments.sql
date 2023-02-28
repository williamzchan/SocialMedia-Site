USE photoshare;
create table comments(
 comment_ID int primary key not null auto_increment,
 comment_text varchar(500),
 commenter varchar(30),
 date_of_comment DATE
 )
