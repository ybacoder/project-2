use pmfkjy5n1gcwlin1;
show tables;
select * from wind_data;

describe wind_data;

create table new_data
select * from wind_data w1;

-- delete d1 from new_data d1
-- inner join new_data d2
-- where
-- 	d1.id > d2.id
-- 	and d1.SCEDTimeStamp = d2.SCEDTimeStamp;
    
-- delete new_data from new_data
-- where SCEDTimeStamp = 0;

select count(*) from new_data;
select count(*) from wind_data;
select count(*) from new_data
	where wind_filename = "";  -- no bueno
select count(*) from wind_data
	where wind_filename = "";
    
