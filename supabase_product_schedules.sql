create table if not exists public.product_schedules (
  id uuid primary key default gen_random_uuid(),
  product_id text not null,
  schedule_date date not null,
  note text not null default '',
  video_count integer not null default 1,
  expected_remaining_count integer not null default 0,
  is_posted boolean not null default false,
  created_at timestamptz not null default now()
);

alter table public.product_schedules
add column if not exists is_posted boolean not null default false;

create index if not exists product_schedules_product_id_idx
on public.product_schedules(product_id);

create index if not exists product_schedules_schedule_date_idx
on public.product_schedules(schedule_date);

insert into public.product_schedules (
  product_id,
  schedule_date,
  note,
  video_count,
  expected_remaining_count
)
select
  id::text,
  scheduled_date,
  coalesce(note, ''),
  1,
  coalesce(remaining_video_count, 0)
from public.products
where scheduled_date is not null
  and not exists (
    select 1
    from public.product_schedules s
    where s.product_id = products.id
      and s.schedule_date = products.scheduled_date
  );
