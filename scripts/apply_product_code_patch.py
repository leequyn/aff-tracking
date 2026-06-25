from pathlib import Path

index = Path('index.html')
text = index.read_text()

def replace_once(old, new):
    global text
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'Missing expected snippet:\n{old[:200]}')
    text = text.replace(old, new, 1)

helpers_old = """    const fmtCurrency = n => new Intl.NumberFormat('vi-VN').format(n||0) + 'đ';
"""
helpers_new = helpers_old + """    const digitsOnly = v => String(v || '').replace(/\D/g, '');
    let productCodeColumnWarningShown = false;
    const isMissingColumnError = (err, col) => {
      const msg = `${err?.message || ''} ${err?.details || ''} ${err?.hint || ''}`.toLowerCase();
      return msg.includes(col.toLowerCase()) && (msg.includes('column') || msg.includes('schema cache'));
    };

    function getProductCode(p) {
      return digitsOnly(p?.product_code);
    }

    function nextProductCode(list) {
      const max = (list || []).reduce((n, p) => {
        const code = Number(getProductCode(p));
        return Number.isFinite(code) ? Math.max(n, code) : n;
      }, 0);
      return String(max + 1);
    }

    async function fetchNextProductCode(exceptId) {
      const { data, error } = await sb.from('products').select('id, product_code');
      if (error && isMissingColumnError(error, 'product_code')) {
        warnMissingProductCodeColumn();
        throw error;
      }
      if (error) throw error;
      return nextProductCode((data || []).filter(p => p.id !== exceptId));
    }

    function warnMissingProductCodeColumn() {
      if (productCodeColumnWarningShown) return;
      productCodeColumnWarningShown = true;
      alert('Cần thêm cột product_code trong bảng products để lưu mã sản phẩm riêng. Mở Supabase SQL Editor và chạy: alter table products add column if not exists product_code text;');
    }

    async function copyText(text) {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        return;
      }
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
"""
replace_once(helpers_old, helpers_new)

replace_once("""      const st = getStatus(p.status);
      const dateRef = useRef();
""", """      const st = getStatus(p.status);
      const dateRef = useRef();
      const [copied, setCopied] = useState(false);
      const productCode = getProductCode(p);
""")

replace_once("""      async function setDate(val) {
        const d = val || null;
        await sb.from('products').update({scheduled_date: d}).eq('id',p.id);
        onUpdate({...p, scheduled_date: d});
      }

      return (
""", """      async function setDate(val) {
        const d = val || null;
        await sb.from('products').update({scheduled_date: d}).eq('id',p.id);
        onUpdate({...p, scheduled_date: d});
      }
      async function copyProductCode() {
        await copyText(productCode);
        setCopied(true);
        setTimeout(() => setCopied(false), 1200);
      }

      return (
""")

replace_once("""              <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold"
""", """              <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                {productCode && <button onClick={copyProductCode} title="Bấm để copy mã sản phẩm"
                  className="text-xs px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1"
                  style={{background:'#ECFDF5', color:'#065F46', border:'1px solid #6EE7B7'}}>
                  <span>#</span>
                  {productCode}
                  <span style={{opacity:.75}}>{copied ? '✓' : '⧉'}</span>
                </button>}
                <span className="text-xs px-2.5 py-0.5 rounded-full font-semibold"
""")

replace_once("""        link:           product?.link||'',
        image_data:     product?.image_data||'',
        channel:        product?.channel||(channels[0]||''),
""", """        link:           product?.link||'',
        image_data:     product?.image_data||'',
        product_code:   product ? getProductCode(product) : '',
        channel:        product?.channel||(channels[0]||''),
""")

replace_once("""      const [saving,     setSaving]     = useState(false);
      const [editCh,     setEditCh]     = useState(false);
      const fileRef = useRef();

      async function moveCh(name, dir) {
""", """      const [saving,     setSaving]     = useState(false);
      const [editCh,     setEditCh]     = useState(false);
      const fileRef = useRef();

      useEffect(() => {
        if (editing || form.product_code) return;
        fetchNextProductCode().then(code => set('product_code', code)).catch(() => {});
      }, []);

      async function moveCh(name, dir) {
""")

replace_once("""        setSaving(true);
        const payload = {
          name:           form.name.trim(),
          link:           form.link.trim(),
          image_data:     form.image_data,
          channel:        ch,
          status:         form.status,
          note:           form.note.trim(),
          scheduled_date: form.scheduled_date || null,
        };
        try {
""", """        setSaving(true);
        try {
          const productCode = digitsOnly(form.product_code) || await fetchNextProductCode(editing ? product.id : null);
          const payload = {
            name:           form.name.trim(),
            link:           form.link.trim(),
            image_data:     form.image_data,
            product_code:   productCode,
            channel:        ch,
            status:         form.status,
            note:           form.note.trim(),
            scheduled_date: form.scheduled_date || null,
          };
""")

replace_once("""            const { data, error } = await sb.from('products').update(payload).eq('id',product.id).select().single();
            if (error) throw error;
""", """            const { data, error } = await sb.from('products').update(payload).eq('id',product.id).select().single();
            if (error && isMissingColumnError(error, 'product_code')) {
              warnMissingProductCodeColumn();
              throw error;
            }
            if (error) throw error;
""")

replace_once("""            const { data, error } = await sb.from('products').insert({...payload, video_count:0, post_today:false}).select().single();
            if (error) throw error;
""", """            const { data, error } = await sb.from('products').insert({...payload, video_count:0, post_today:false}).select().single();
            if (error && isMissingColumnError(error, 'product_code')) {
              warnMissingProductCodeColumn();
              throw error;
            }
            if (error) throw error;
""")

replace_once("""              {/* Image */}
""", """              {/* Product code */}
              <div>
                <label className="text-xs font-bold mb-1.5 block tracking-wide uppercase" style={{color:'var(--muted)'}}>Mã sản phẩm</label>
                <div className="flex gap-2">
                  <input value={form.product_code} onChange={e=>set('product_code',digitsOnly(e.target.value))}
                    placeholder="Chỉ nhập số"
                    inputMode="numeric"
                    className="flex-1 px-4 py-3 rounded-2xl text-sm outline-none font-bold"
                    style={{background:'var(--bg)', color:'var(--text)', border:'1.5px solid var(--border)'}} />
                  <button onClick={async()=>set('product_code', await fetchNextProductCode(editing ? product.id : null))}
                    className="px-4 py-3 rounded-2xl text-sm font-bold flex-shrink-0"
                    style={{background:'var(--p-light)', color:'var(--primary)', border:'1.5px solid var(--border)'}}>
                    Tạo mã
                  </button>
                </div>
              </div>

              {/* Image */}
""")

replace_once("""      async function fetchAll() {
        const { data } = await sb.from('products').select('*').order('created_at', { ascending: false });
        if (data) setProducts(data);
      }

      async function fetchChannels() {
""", """      async function fetchAll() {
        const { data } = await sb.from('products').select('*').order('created_at', { ascending: false });
        if (data) setProducts(await ensureProductCodes(data));
      }

      async function ensureProductCodes(list) {
        const usedCodes = new Set(list.map(getProductCode).filter(Boolean));
        let nextCode = Math.max(0, ...Array.from(usedCodes).map(c => Number(c) || 0)) + 1;
        let changed = false;
        const next = list.map(p => {
          if (getProductCode(p)) return p;
          changed = true;
          while (usedCodes.has(String(nextCode))) nextCode++;
          const product_code = String(nextCode++);
          usedCodes.add(product_code);
          return {...p, product_code};
        });
        if (!changed) return next;

        const updates = next
          .filter(p => !getProductCode(list.find(x => x.id === p.id)))
          .map(p => sb.from('products').update({product_code: p.product_code}).eq('id', p.id));
        const results = await Promise.all(updates);
        if (results.some(r => isMissingColumnError(r.error, 'product_code'))) {
          warnMissingProductCodeColumn();
          return list;
        }
        return next;
      }

      async function fetchChannels() {
""")

index.write_text(text)

Path('supabase_product_code.sql').write_text("""alter table public.products
add column if not exists product_code text;

create unique index if not exists products_product_code_key
on public.products (product_code)
where product_code is not null;
""")

Path('backfill_product_codes.sql').write_text("""with numbered_products as (
  select
    id,
    row_number() over (order by created_at, id) as rn
  from public.products
)
update public.products p
set product_code = n.rn::text
from numbered_products n
where p.id = n.id;
""")
