-- Run in the Supabase SQL Editor before using the Chia lợi nhuận section.
-- If your project uses the newer Data API exposure setting, also enable this table
-- in Dashboard → Project Settings → Data API → Exposed schemas/tables.
create table if not exists public.profit_distributions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid(),
  date date not null default current_date,
  recipient text not null,
  channel text not null default '',
  amount numeric not null check (amount > 0),
  note text not null default '',
  created_at timestamptz not null default now()
);

alter table public.profit_distributions enable row level security;

grant usage on schema public to authenticated;
grant select, insert, update, delete on public.profit_distributions to authenticated;

do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'profit_distributions' and policyname = 'profit distributions owner select') then
    create policy "profit distributions owner select" on public.profit_distributions for select to authenticated using (user_id = (select auth.uid()));
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'profit_distributions' and policyname = 'profit distributions owner insert') then
    create policy "profit distributions owner insert" on public.profit_distributions for insert to authenticated with check (user_id = (select auth.uid()));
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'profit_distributions' and policyname = 'profit distributions owner update') then
    create policy "profit distributions owner update" on public.profit_distributions for update to authenticated using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'profit_distributions' and policyname = 'profit distributions owner delete') then
    create policy "profit distributions owner delete" on public.profit_distributions for delete to authenticated using (user_id = (select auth.uid()));
  end if;
end $$;

create index if not exists profit_distributions_date_idx on public.profit_distributions(date);
create index if not exists profit_distributions_channel_idx on public.profit_distributions(channel);

notify pgrst, 'reload schema';
