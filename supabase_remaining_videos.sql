alter table public.products
add column if not exists remaining_video_count integer not null default 0;

update public.products
set remaining_video_count = 0
where remaining_video_count is null;
