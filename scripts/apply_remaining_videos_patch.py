from pathlib import Path

index = Path('index.html')
text = index.read_text()

def replace_once(old, new):
    global text
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'Missing expected snippet:\n{old[:240]}')
    text = text.replace(old, new, 1)

replace_once("""    function warnMissingProductCodeColumn() {
      if (productCodeColumnWarningShown) return;
      productCodeColumnWarningShown = true;
      alert('Cần thêm cột product_code trong bảng products để lưu mã sản phẩm riêng. Mở Supabase SQL Editor và chạy: alter table products add column if not exists product_code text;');
    }

    async function copyText(text) {
""", """    function warnMissingProductCodeColumn() {
      if (productCodeColumnWarningShown) return;
      productCodeColumnWarningShown = true;
      alert('Cần thêm cột product_code trong bảng products để lưu mã sản phẩm riêng. Mở Supabase SQL Editor và chạy: alter table products add column if not exists product_code text;');
    }

    function warnMissingRemainingVideosColumn() {
      alert('Cần thêm cột remaining_video_count trong bảng products để lưu số video còn lại. Mở Supabase SQL Editor và chạy file supabase_remaining_videos.sql trong repo.');
    }

    async function copyText(text) {
""")

replace_once("""      async function changeVideoCount(delta) {
        const v = Math.max(0,(p.video_count||0)+delta);
        await sb.from('products').update({video_count:v}).eq('id',p.id);
        onUpdate({...p, video_count:v});
      }
      async function setDate(val) {
""", """      async function changeVideoCount(delta) {
        const v = Math.max(0,(p.video_count||0)+delta);
        await sb.from('products').update({video_count:v}).eq('id',p.id);
        onUpdate({...p, video_count:v});
      }
      async function changeRemainingVideoCount(delta) {
        const v = Math.max(0,(p.remaining_video_count||0)+delta);
        const { error } = await sb.from('products').update({remaining_video_count:v}).eq('id',p.id);
        if (error && isMissingColumnError(error, 'remaining_video_count')) return warnMissingRemainingVideosColumn();
        if (error) return alert('Lỗi lưu số video còn lại: ' + error.message);
        onUpdate({...p, remaining_video_count:v});
      }
      async function setDate(val) {
""")

replace_once("""              <span className="text-xs ml-0.5 font-medium" style={{color:'var(--muted)'}}>video</span>
            </div>

            {/* Scheduled date picker */}
""", """              <span className="text-xs ml-0.5 font-medium" style={{color:'var(--muted)'}}>video</span>
            </div>

            {/* Remaining video counter */}
            <div className="flex items-center gap-1.5 rounded-xl px-2 py-1.5" style={{background:'#ECFDF5', border:'1.5px solid #6EE7B7'}}>
              <button onClick={()=>changeRemainingVideoCount(-1)}
                className="w-5 h-5 rounded-md flex items-center justify-center font-bold text-xs"
                style={{background:'var(--card)', color:'#047857', boxShadow:'0 1px 3px rgba(0,0,0,0.1)'}}>−</button>
              <span className="text-sm font-bold min-w-[1.2rem] text-center" style={{color:'#065F46'}}>{p.remaining_video_count||0}</span>
              <button onClick={()=>changeRemainingVideoCount(1)}
                className="w-5 h-5 rounded-md flex items-center justify-center font-bold text-xs"
                style={{background:'var(--card)', color:'#047857', boxShadow:'0 1px 3px rgba(0,0,0,0.1)'}}>+</button>
              <span className="text-xs ml-0.5 font-bold" style={{color:'#047857'}}>còn</span>
            </div>

            {/* Scheduled date picker */}
""")

replace_once("""        new_channel:    '',
        status:         product?.status||'chua_ro',
        note:           product?.note||'',
""", """        new_channel:    '',
        status:         product?.status||'chua_ro',
        remaining_video_count: product?.remaining_video_count||0,
        note:           product?.note||'',
""")

replace_once("""            product_code:   productCode,
            channel:        ch,
            status:         form.status,
            note:           form.note.trim(),
""", """            product_code:   productCode,
            channel:        ch,
            status:         form.status,
            remaining_video_count: Number(digitsOnly(form.remaining_video_count)),
            note:           form.note.trim(),
""")

replace_once("""            if (error && isMissingColumnError(error, 'product_code')) {
              warnMissingProductCodeColumn();
              throw error;
            }
            if (error) throw error;
            onSave(data);
          } else {
""", """            if (error && isMissingColumnError(error, 'product_code')) {
              warnMissingProductCodeColumn();
              throw error;
            }
            if (error && isMissingColumnError(error, 'remaining_video_count')) {
              warnMissingRemainingVideosColumn();
              throw error;
            }
            if (error) throw error;
            onSave(data);
          } else {
""")

replace_once("""            if (error && isMissingColumnError(error, 'product_code')) {
              warnMissingProductCodeColumn();
              throw error;
            }
            if (error) throw error;
            onSave(data);
          }
""", """            if (error && isMissingColumnError(error, 'product_code')) {
              warnMissingProductCodeColumn();
              throw error;
            }
            if (error && isMissingColumnError(error, 'remaining_video_count')) {
              warnMissingRemainingVideosColumn();
              throw error;
            }
            if (error) throw error;
            onSave(data);
          }
""")

replace_once("""              {/* Note */}
              <div>
                <label className="text-xs font-bold mb-1.5 block tracking-wide uppercase" style={{color:'var(--muted)'}}>Ghi chú</label>
""", """              {/* Remaining videos */}
              <div>
                <label className="text-xs font-bold mb-1.5 block tracking-wide uppercase" style={{color:'var(--muted)'}}>Video còn lại chưa đăng</label>
                <input value={form.remaining_video_count} onChange={e=>set('remaining_video_count',digitsOnly(e.target.value))}
                  placeholder="VD: 3"
                  inputMode="numeric"
                  className="w-full px-4 py-3 rounded-2xl text-sm outline-none font-bold"
                  style={{background:'#ECFDF5', color:'#065F46', border:'1.5px solid #6EE7B7'}} />
              </div>

              {/* Note */}
              <div>
                <label className="text-xs font-bold mb-1.5 block tracking-wide uppercase" style={{color:'var(--muted)'}}>Ghi chú</label>
""")

replace_once("""            if (activeStatus === 'post_today') return p.post_today || p.scheduled_date === today;
            if (activeStatus === 'tomorrow')   return p.scheduled_date === TOMORROW;
            if (activeStatus === 'all')        return true;
""", """            if (activeStatus === 'post_today') return p.post_today || p.scheduled_date === today;
            if (activeStatus === 'tomorrow')   return p.scheduled_date === TOMORROW;
            if (activeStatus === 'remaining_videos') return (p.remaining_video_count || 0) > 0;
            if (activeStatus === 'all')        return true;
""")

replace_once("""        all:        chFiltered.length,
        post_today: chFiltered.filter(p => p.post_today || p.scheduled_date === today).length,
        tomorrow:   chFiltered.filter(p => p.scheduled_date === TOMORROW).length,
        ...Object.fromEntries(STATUSES.map(s => [s.id, chFiltered.filter(p => p.status === s.id).length])),
""", """        all:        chFiltered.length,
        post_today: chFiltered.filter(p => p.post_today || p.scheduled_date === today).length,
        tomorrow:   chFiltered.filter(p => p.scheduled_date === TOMORROW).length,
        remaining_videos: chFiltered.filter(p => (p.remaining_video_count || 0) > 0).length,
        ...Object.fromEntries(STATUSES.map(s => [s.id, chFiltered.filter(p => p.status === s.id).length])),
""")

replace_once("""        { id:'all',        label:'Tất cả' },
        { id:'post_today', label:'📌 Hôm nay' },
        { id:'tomorrow',   label:'📅 Ngày mai' },
        ...STATUSES.map(s=>({id:s.id, label:s.label, dot:s.dot, bg:s.bg, fg:s.fg, ring:s.ring})),
""", """        { id:'all',        label:'Tất cả' },
        { id:'post_today', label:'📌 Hôm nay' },
        { id:'tomorrow',   label:'📅 Ngày mai' },
        { id:'remaining_videos', label:'Còn video', dot:'#10B981', bg:'#ECFDF5', fg:'#065F46', ring:'#6EE7B7' },
        ...STATUSES.map(s=>({id:s.id, label:s.label, dot:s.dot, bg:s.bg, fg:s.fg, ring:s.ring})),
""")

index.write_text(text)

Path('supabase_remaining_videos.sql').write_text("""alter table public.products
add column if not exists remaining_video_count integer not null default 0;

update public.products
set remaining_video_count = 0
where remaining_video_count is null;
""")
