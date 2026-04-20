# mdnice 主文 CSS（合并版）

```css
:root{
  --primary:#0052D9;
  --secondary:#E34D59;
  --bg:#F7F9FC;
  --text:#333;
  --muted:#6B7280;
}

#write{
  color:var(--text);
  font-size:16px;
  line-height:1.75;
}
#write p{ margin:8px 0; }
#write strong{ color:#111; }

#write h1{
  font-size:22px;
  color:var(--primary);
  text-align:center;
  font-weight:800;
  margin:6px 0 18px;
}
#write h2{
  background:linear-gradient(90deg,#E6F0FF 0%, #FFFFFF 100%);
  border-left:5px solid var(--primary);
  padding:10px 14px;
  margin:26px 0 16px;
  font-size:18px;
  color:#000;
  border-radius:0 4px 4px 0;
}
#write h3{
  font-size:16px;
  color:var(--primary);
  margin:16px 0 6px;
  font-weight:700;
}

#write .meta-card, #write .core-card{
  background:#F2F6FB;
  border-radius:10px;
  padding:12px 14px;
  margin:10px 0 14px;
  box-shadow:0 2px 6px rgba(0,0,0,0.04);
}
#write .meta-card{ font-size:14px; color:var(--muted); }
#write .meta-card strong{ color:#111; }
#write .core-card{ font-size:15px; color:#222; }

#write blockquote{
  background:#F2F5FA;
  border-left:4px solid var(--primary);
  border-radius:8px;
  padding:12px 14px;
  margin:12px 0;
  color:#555;
  font-size:15px;
  line-height:1.6;
  box-shadow:0 2px 6px rgba(0,0,0,0.05);
}
#write blockquote strong{ color:var(--primary); }

#write a{
  color:var(--primary);
  text-decoration:none;
  border-bottom:1px dashed var(--primary);
}

#write hr{
  border:none;
  height:1px;
  background:#E0E0E0;
  margin:24px 0;
  position:relative;
}
#write hr::after{
  content:"DARE TO B2B";
  position:absolute;
  left:50%;
  top:50%;
  transform:translate(-50%,-50%);
  background:#fff;
  padding:0 10px;
  color:#c9c9c9;
  font-size:12px;
}

#write ul, #write ol{
  padding-left:20px;
  color:#444;
}
#write li{ margin:6px 0; line-height:1.6; }

#write code{
  background:#FFF3E0;
  color:#E65100;
  padding:2px 4px;
  border-radius:3px;
  font-family:Menlo, Monaco, Consolas, "Courier New", monospace;
}
```
