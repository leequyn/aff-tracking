from pathlib import Path

path = Path('index.html')
text = path.read_text()
old = "<span className=\"text-xs ml-0.5 font-medium\" style={{color:'var(--muted)'}}>video</span>"
new = "<span className=\"text-xs ml-0.5 font-medium\" style={{color:'var(--muted)'}}>đăng</span>"
if old not in text and new not in text:
    raise SystemExit('Video label snippet not found')
path.write_text(text.replace(old, new, 1))
