-- Cyber Security Lab: jalankan satu kali di SQL Editor proyek Anda.
-- Hanya menyimpan laporan dan hasil latihan; fixture rentan tetap di simulator.
begin;
create table public.cyber_lab_findings (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade default auth.uid(),
 lab_id text not null check (char_length(lab_id) between 1 and 60),
 title text not null check (char_length(title) between 1 and 180),
 severity text not null check (severity in ('Informational','Low','Medium','High','Critical')),
 status text not null check (status in ('Open','In progress','Fixed','Retest passed')),
 steps text not null check (char_length(steps) between 1 and 10000),
 evidence text not null check (char_length(evidence) between 1 and 20000),
 impact text not null check (char_length(impact) between 1 and 10000),
 remediation text not null check (char_length(remediation) between 1 and 10000),
 created_at timestamptz not null default now()
);
create table public.cyber_lab_runs (
 id uuid primary key default gen_random_uuid(),
 user_id uuid not null references auth.users(id) on delete cascade default auth.uid(),
 lab_id text not null check (char_length(lab_id) between 1 and 60),
 mode text not null check (mode in ('vulnerable','fixed')),
 input text not null check (char_length(input) <= 4000),
 result jsonb not null check (octet_length(result::text) <= 30000),
 created_at timestamptz not null default now()
);
create index cyber_lab_findings_user_date on public.cyber_lab_findings(user_id,created_at desc);
create index cyber_lab_runs_user_date on public.cyber_lab_runs(user_id,created_at desc);
alter table public.cyber_lab_findings enable row level security;
alter table public.cyber_lab_runs enable row level security;
revoke all on public.cyber_lab_findings,public.cyber_lab_runs from anon,authenticated;
grant select,insert,update on public.cyber_lab_findings to authenticated;
grant select,insert on public.cyber_lab_runs to authenticated;
create policy findings_read_own on public.cyber_lab_findings for select to authenticated using ((select auth.uid())=user_id);
create policy findings_insert_own on public.cyber_lab_findings for insert to authenticated with check ((select auth.uid())=user_id);
create policy findings_update_own on public.cyber_lab_findings for update to authenticated using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id);
create policy runs_read_own on public.cyber_lab_runs for select to authenticated using ((select auth.uid())=user_id);
create policy runs_insert_own on public.cyber_lab_runs for insert to authenticated with check ((select auth.uid())=user_id);
commit;
