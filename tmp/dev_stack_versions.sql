-- dev-stack template versions: which contain filegator vs blinko
select
  tv.name,
  tv.created_at,
  tv.archived,
  count(*) filter (where tvf.content like '%filegator%') as filegator_refs,
  count(*) filter (where tvf.content like '%blinko%') as blinko_refs
from template_versions tv
join templates t on t.id = tv.template_id
left join template_version_files tvf on tvf.template_version_id = tv.id
where t.name = 'dev-stack'
group by tv.name, tv.created_at, tv.archived
order by tv.created_at desc
limit 6;
