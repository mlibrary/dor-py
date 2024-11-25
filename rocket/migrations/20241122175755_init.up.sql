-- Add up migration script here
DROP TABLE IF EXISTS `tickets`;
CREATE TABLE `tickets` (
                           `id` varchar(32) NOT NULL,
                           `created_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                           PRIMARY KEY (`id`)
);
