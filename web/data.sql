/**
* Extracts number of mails sent to a team (by a person) mailing list monthly.
* 
* Sample output for 'teammetrics-discuss' and 'Sukhbir Singh'
*
* year | month | count 
* ------+-------+-------
* 2011 |     5 |     7
* 2011 |     6 |    76
* 2011 |     7 |    55
* 2011 |     8 |   116
* 2011 |     9 |    48
* 2011 |    10 |    33
* 2011 |    11 |    17
* 2011 |    12 |    34
* 2012 |     1 |    31
* 2012 |     2 |    26
* 2012 |     3 |    18
* 2012 |     4 |     5
*
* By modifying 'and name = xxx' in the query, separate results like top5, top10 
* total can be achieved.
*/

select 
	extract(year from archive_date) as year,
	extract(month from archive_date) as month,
	count(*)
from
	listarchives
where
		extract(year from archive_date) in 
			(select
				distinct extract(year from archive_date)
			from
				listarchives
			where
					project = 'teammetrics-discuss')
	and
		project='teammetrics-discuss'
	and
		name = 'Sukhbir Singh'
group by
	year,
	month
order by
	year;

