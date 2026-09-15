import gradio as gr
import subprocess
import os

current_process = None

def start_stream(m3u8_url, url_1, key_1, url_2, key_2, url_3, key_3, quality, logo_file, ticker_text, ticker_dir, ticker_color, ticker_bg, ticker_opacity, clock_show, clock_pos, clock_color, clock_bg, clock_opacity):
    global current_process
    
    if current_process is not None:
        stop_stream()

    if not m3u8_url:
        return "❌ هەڵە: تکایە بەستەری سەرچاوەی M3U8 بەتاڵ مەجێهێڵە!"

    destinations = []
    
    if url_1 and key_1:
        sep = "" if url_1.strip().endswith("/") else "/"
        destinations.append(f"[f=flv]{url_1.strip()}{sep}{key_1.strip()}")
        
    if url_2 and key_2:
        sep = "" if url_2.strip().endswith("/") else "/"
        destinations.append(f"[f=flv]{url_2.strip()}{sep}{key_2.strip()}")
        
    if url_3 and key_3:
        sep = "" if url_3.strip().endswith("/") else "/"
        destinations.append(f"[f=flv]{url_3.strip()}{sep}{key_3.strip()}")

    if not destinations:
        return "❌ هەڵە: تکایە لانی کەم بەستەر و کلیلی یەک پلاتفۆرم پڕبکەرەوە!"

    tee_output = "|".join(destinations)
    command = ["ffmpeg", "-re", "-i", m3u8_url]
    filters = []
    inputs = []

    if logo_file is not None:
        inputs.extend(["-i", logo_file.name])
        filters.append("delogo=x=w-250:y=10:w=240:h=100")
        filters.append("overlay=main_w-overlay_w-20:20")

    if ticker_text:
        x_pos = "w-mod(t*75\,w+tw)" if ticker_dir == "ڕاست بۆ چەپ (RTL)" else "mod(t*75\,w+tw)-tw"
        box_color = f"{ticker_bg}@{ticker_opacity}"
        filters.append(f"drawtext=text='{ticker_text}':fontcolor={ticker_color}:fontsize=24:box=1:boxcolor={box_color}:boxborderw=5:x={x_pos}:y=h-40")

    if clock_show:
        if clock_pos == "سەرەوە - چەپ": c_x, c_y = "20", "20"
        elif clock_pos == "سەرەوە - ڕاست": c_x, c_y = "w-tw-20", "120" if logo_file else "20"
        elif clock_pos == "خوارەوە - چەپ": c_x, c_y = "20", "h-th-60"
        else: c_x, c_y = "w-tw-20", "h-th-60"
        c_box = f"{clock_bg}@{clock_opacity}"
        filters.append(f"drawtext=text='%{{localtime\\:%H\\\\:%M\\\\:%S}}':fontcolor={clock_color}:fontsize=30:box=1:boxcolor={c_box}:x={c_x}:y={c_y}")

    if quality != "وەک خۆی بمێنێتەوە (بێ گۆڕانکاری)":
        if quality == "1080p (FHD)": filters.append("scale=-2:1080")
        elif quality == "720p (HD)": filters.append("scale=-2:720")
        elif quality == "480p (SD)": filters.append("scale=-2:480")
        elif quality == "360p (Low)": filters.append("scale=-2:360")

    if filters:
        command.extend(["-filter_complex", ",".join(filters)])
        command.extend(["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28"])
    else:
        command.extend(["-c:v", "copy"])

    command.extend([
        "-c:a", "aac", "-b:a", "128k",
        "-f", "tee", tee_output
    ])

    try:
        current_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return f"▶️ پەخشەکە دەستی پێکرد! ڤیدیۆکە لە یەک کاتدا بۆ {len(destinations)} پلاتفۆرم دەنێردرێت."
    except Exception as e:
        return f"❌ هەڵەیەک ڕوویدا: {str(e)}"

def stop_stream():
    global current_process
    if current_process is not None:
        current_process.terminate()
        current_process = None
        return "⏹️ پەخشەکە وەستێنرا."
    return "هیچ پەخشێک لە کارکردندا نییە."

with gr.Blocks(title="Master Control Room", css="body {font-family: Arial, sans-serif; direction: rtl;}") as demo:
    gr.Markdown("## 📺 ژووری کۆنتڕۆڵ و ڕیستریم")
    
    with gr.Row():
        m3u8_input = gr.Textbox(label="بەستەری سەرچاوە (M3U8 ئەسڵی)", placeholder="لینکە ئەسڵییەکە لێرە دابنێ...")

    with gr.Accordion("📡 شوێنی ناردنی پەخش (RTMP Destinations)", open=True):
        gr.Markdown("### ١. پلاتفۆرمی یەکەم (پێویستە)")
        with gr.Row():
            url_1 = gr.Textbox(label="بەستەری سێرڤەر (URL)", placeholder="rtmp://...")
            key_1 = gr.Textbox(label="کلیلی پەخش (Stream Key)", placeholder="...")
            
        gr.Markdown("### ٢. پلاتفۆرمی دووەم (ئارەزوومەندانە)")
        with gr.Row():
            url_2 = gr.Textbox(label="بەستەری سێرڤەر (URL)", placeholder="")
            key_2 = gr.Textbox(label="کلیلی پەخش (Stream Key)", placeholder="")

        gr.Markdown("### ٣. پلاتفۆرمی سێیەم (ئارەزوومەندانە)")
        with gr.Row():
            url_3 = gr.Textbox(label="بەستەری سێرڤەر (URL)", placeholder="")
            key_3 = gr.Textbox(label="کلیلی پەخش (Stream Key)", placeholder="")

    with gr.Accordion("⚙️ ڕێکخستنی کوالێتی ڤیدیۆ", open=False):
        quality_input = gr.Dropdown(choices=["وەک خۆی بمێنێتەوە (بێ گۆڕانکاری)", "1080p (FHD)", "720p (HD)", "480p (SD)", "360p (Low)"], value="وەک خۆی بمێنێتەوە (بێ گۆڕانکاری)", label="هەڵبژاردنی کوالێتی")

    with gr.Accordion("🖼️ ڕێکخستنی لۆگۆ", open=False):
        logo_input = gr.File(label="وێنەی لۆگۆ (PNG)", file_types=[".png"])

    with gr.Accordion("📰 ڕێکخستنی شریتی هەواڵ", open=False):
        ticker_input = gr.Textbox(label="نووسینی هەواڵەکان", placeholder="...")
        with gr.Row():
            ticker_dir = gr.Dropdown(choices=["ڕاست بۆ چەپ (RTL)", "چەپ بۆ ڕاست (LTR)"], value="ڕاست بۆ چەپ (RTL)", label="ئاڕاستەی جوڵە")
            ticker_color = gr.Dropdown(choices=["yellow", "white", "red", "green", "black"], value="yellow", label="ڕەنگی نووسین")
        with gr.Row():
            ticker_bg = gr.Dropdown(choices=["black", "blue", "red", "green", "white"], value="black", label="ڕەنگی بۆکس")
            ticker_opacity = gr.Slider(minimum=0.1, maximum=1.0, value=0.5, step=0.1, label="شەفافیەتی بۆکس")

    with gr.Accordion("⏰ ڕێکخستنی کاتژمێر", open=False):
        clock_show = gr.Checkbox(label="پیشاندانی کاتژمێر", value=True)
        with gr.Row():
            clock_pos = gr.Dropdown(choices=["سەرەوە - چەپ", "سەرەوە - ڕاست", "خوارەوە - چەپ", "خوارەوە - ڕاست"], value="سەرەوە - چەپ", label="شوێن")
            clock_color = gr.Dropdown(choices=["white", "yellow", "red", "green", "black"], value="white", label="ڕەنگ")
        with gr.Row():
            clock_bg = gr.Dropdown(choices=["black", "blue", "red", "green", "white"], value="black", label="باکگراوند")
            clock_opacity = gr.Slider(minimum=0.0, maximum=1.0, value=0.5, step=0.1, label="شەفافیەت")

    with gr.Row():
        start_btn = gr.Button("▶️ دەستپێکردنی پەخش", variant="primary")
        stop_btn = gr.Button("⏹️ وەستاندن", variant="stop")
        
    status_output = gr.Textbox(label="دۆخی سێرڤەر", interactive=False)
    
    start_btn.click(start_stream, inputs=[m3u8_input, url_1, key_1, url_2, key_2, url_3, key_3, quality_input, logo_input, ticker_input, ticker_dir, ticker_color, ticker_bg, ticker_opacity, clock_show, clock_pos, clock_color, clock_bg, clock_opacity], outputs=[status_output])
    stop_btn.click(stop_stream, inputs=[], outputs=[status_output])

# بەکارهێنانی پۆرتی Render بۆ کارکردن
port = int(os.environ.get("PORT", 10000))
demo.launch(server_name="0.0.0.0", server_port=port)
