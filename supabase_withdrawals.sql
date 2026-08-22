create table if not exists public.withdrawals (
  id uuid primary key default gen_random_uuid(),
  date date not null default current_date,
  channel text not null,
  amount numeric not null default 0,
  note text not null default '',
  created_at timestamptz not null default now()
);

alter table public.withdrawals
add column if not exists note text not null default '';

create index if not exists withdrawals_date_idx
on public.withdrawals(date);

create index if not exists withdrawals_channel_idx
on public.withdrawals(channel);

notify pgrst, 'reload schema';
