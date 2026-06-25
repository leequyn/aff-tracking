with numbered_products as (
  select
    id,
    row_number() over (order by created_at, id) as rn
  from public.products
)
update public.products p
set product_code = n.rn::text
from numbered_products n
where p.id = n.id;
