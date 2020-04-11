/* this script can be used to make corrections to the database if necessary. */
/* for example, remove duplicate SCEDTimeStamp rows. (code included for this.) */

use pmfkjy5n1gcwlin1;
show tables;
select * from wind_data;
/* Export to CSV as a backup */

create table new_data like wind_data;
insert into new_data
select * from wind_data;
    
/* delete duplicate rows from new_data */
delete d1 from new_data d1
inner join new_data d2
where
	d1.id > d2.id
	and d1.SCEDTimeStamp = d2.SCEDTimeStamp;

/* due to lack of DB space, need to drop wind_data before renaming new_data to "wind_data" */
select
	table_schema,
    sum((data_length+index_length)/1024/1024) AS MB
from information_schema.tables
group by 1;  -- check storage usage if necessary
-- drop table wind_data;

create table wind_data like new_data;
insert into wind_data
select * from new_data;

/* preserve space */
-- drop table new_data;

