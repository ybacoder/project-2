use pmfkjy5n1gcwlin1;
show tables;
select * from wind_data;

describe wind_data;

/* copy to separate table for cleaning */
create table new_data
select * from wind_data w1;

/* delete duplicate rows from new_data */
-- delete d1 from new_data d1
-- inner join new_data d2
-- where
-- 	d1.id > d2.id
-- 	and d1.SCEDTimeStamp = d2.SCEDTimeStamp;

/* also delete "nonsense" rows--I don't know where these came from; hope we figure it out so we prevent it from happening again. */
-- delete new_data from new_data
-- where SCEDTimeStamp = 0;

/* know thy dataset */
select count(*) from new_data;
select count(*) from wind_data;
select count(*) from new_data
	where wind_filename = "";
select count(*) from wind_data
	where wind_filename = "";

/**
couldn't rename for some reason;
got error "INSERT command denied to user 'k2u1yqycv3bodj4z'@'ec2-3-87-139-51.compute-1.amazonaws.com' for table 'new_data'"
... as well as for 'wind_data'.
next step was to check storage used.
**/
select table_schema, sum((data_length+index_length)/1024/1024) AS MB from information_schema.tables group by 1;
/* storage used at this time (with two tables) was over the 0.005 GB limit. */

/* due to inability to rename, dropped wind_data table (only after exporting to CSV, just in case!) */
-- drop table wind_data;
-- show tables;

/* recreate wind_data from new_data */
create table wind_data
select * from new_data n1;

/* again, only after exporting to CSV */
select * from new_data;
drop table new_data;