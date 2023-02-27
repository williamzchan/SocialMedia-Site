ALTER TABLE `photoshare`.`users` 
ADD COLUMN `first_name` VARCHAR(45) AFTER `password`,
ADD COLUMN `last_name` VARCHAR(45) AFTER `first_name`,
ADD COLUMN `dob` DATE AFTER `last_name`,
ADD COLUMN `hometown` VARCHAR(100) AFTER `dob`,
ADD COLUMN `gender` varchar(20) AFTER `hometown`;