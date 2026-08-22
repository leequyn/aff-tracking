create table if not exists public.withdrawals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid default auth.uid(),
  date date not null default current_date,
  channel text not null,
  amount numeric not null default 0,
  note text not null default '',
  created_at timestamptz not null default now()
);

alter table public.withdrawals
add column if not exists note text not null default '';

alter table public.withdrawals
add column if not exists user_id uuid default auth.uid();

alter table public.withdrawals enable row level security;

grant usage on schema public to authenticated;
grant select, insert, update, delete on public.withdrawals to authenticated;

do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'withdrawals'
      and policyname = 'withdrawals owner select'
  ) then
    create policy "withdrawals owner select"
    on public.withdrawals
    for select
    to authenticated
    using (user_id = (select auth.uid()));
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'withdrawals'
      and policyname = 'withdrawals owner insert'
  ) then
    create policy "withdrawals owner insert"
    on public.withdrawals
    for insert
    to authenticated
    with check (user_id = (select auth.uid()));
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'withdrawals'
      and policyname = 'withdrawals owner update'
  ) then
    create policy "withdrawals owner update"
    on public.withdrawals
    for update
    to authenticated
    using (user_id = (select auth.uid()))
    with check (user_id = (select auth.uid()));
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname = 'public'
      and tablename = 'withdrawals'
      and policyname = 'withdrawals owner delete'
  ) then
    create policy "withdrawals owner delete"
    on public.withdrawals
    for delete
    to authenticated
    using (user_id = (select auth.uid()));
  end if;
end $$;

create index if not exists withdrawals_date_idx
on public.withdrawals(date);

create index if not exists withdrawals_channel_idx
on public.withdrawals(channel);

notify pgrst, 'reload schema';
