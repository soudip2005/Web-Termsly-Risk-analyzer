from flask import Flask, render_template, request, send_file, jsonify
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64
import re
import threading
import uuid
from urllib.parse import urlparse

# Import your existing core logic
import core.scraper as scraper
import core.analyzer as analyzer
import core.processor as processor
import core.pdf_generator as pdf_generator

app = Flask(__name__)

RESULT_CACHE = {}
TASKS = {} # Global dictionary to track background threads

def run_analysis_worker(base_url, target_lang, task_id):
    """Runs in the background and updates the TASKS dictionary in real-time."""
    results = {}
    try:
        # Step 1: Find and Scrape
        TASKS[task_id]['status'] = f"🔍 Searching for policy pages on {base_url}..."
        policy_urls = scraper.find_policy_links(base_url)
        if not policy_urls:
            TASKS[task_id]['error'] = f"Could not find any policy pages for {base_url}"
            TASKS[task_id]['complete'] = True
            return
        
        main_policy_url = policy_urls[0]
        results['url'] = main_policy_url

        # Step 2: Extract Text
        TASKS[task_id]['status'] = f"📄 Extracting text from {main_policy_url}..."
        full_text, error = scraper.extract_text_from_url(main_policy_url)
        if error or not full_text:
            TASKS[task_id]['error'] = f"Text extraction failed: {error}"
            TASKS[task_id]['complete'] = True
            return
        results['full_text'] = full_text

        # Step 3: Analyze Risk
        TASKS[task_id]['status'] = "🤖 Analyzing risk factors..."
        overall_risk, highlights = analyzer.analyze_risk(full_text)
        results['overall_risk'] = overall_risk
        results['highlights'] = highlights

        # Step 4: Summarize
        TASKS[task_id]['status'] = "📝 Generating executive summary..."
        summary_en = processor.summarize_text(full_text)
        results['summary'] = summary_en

        # Step 5: Translate
        TASKS[task_id]['status'] = f"🌐 Translating to {target_lang.capitalize()}..."
        summary_translated = processor.translate_text(summary_en, target_lang)
        results['translated_summary'] = summary_translated
        results['language'] = target_lang.capitalize()

        # Mark as finished
        TASKS[task_id]['results'] = results
        TASKS[task_id]['complete'] = True

    except Exception as e:
        TASKS[task_id]['error'] = f"An error occurred: {str(e)}"
        TASKS[task_id]['complete'] = True

def count_sentences(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 5]
    return len(sentences)

def calculate_counts(highlights, full_text):
    total_sentences = count_sentences(full_text)
    high_count = sum(1 for h in highlights if "[HIGH RISK]" in h)
    medium_count = sum(1 for h in highlights if "[MEDIUM RISK]" in h)
    low_count = max(0, total_sentences - high_count - medium_count)
    return high_count, medium_count, low_count

def create_pie_chart_base64(high_count, medium_count, low_count):
    labels = ['High Risk', 'Medium Risk', 'Low Risk (Safe)']
    sizes = [high_count, medium_count, low_count]
    colors = ['#ef4444', '#f59e0b', '#22c55e']

    final_labels, final_sizes, final_colors = [], [], []
    for l, s, c in zip(labels, sizes, colors):
        if s > 0:
            final_labels.append(l)
            final_sizes.append(s)
            final_colors.append(c)
            
    if not final_sizes:
        return None

    max_val = max(final_sizes)
    max_idx = final_sizes.index(max_val)
    explode = [0.1 if i == max_idx else 0 for i in range(len(final_sizes))]

    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_alpha(0)
    
    wedges, texts, autotexts = ax.pie(
        final_sizes, labels=final_labels, autopct='%1.1f%%', 
        startangle=90, colors=final_colors, explode=explode, 
        textprops={'fontsize': 10, 'color': '#333'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 1}
    )
    
    for i, wedge in enumerate(wedges):
        wedge.set_alpha(1.0 if i == max_idx else 0.3)
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_weight('bold')

    ax.axis('equal')
    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig) 
    return image_base64

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start_analysis():
    """Starts the background thread and returns the tracking ID."""
    url_input = request.form.get("domain")
    lang_input = request.form.get("language")
    
    domain = urlparse(url_input).netloc
    if not domain:
        domain = urlparse(f"https://{url_input}").netloc
        
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {'status': 'Initializing...', 'complete': False, 'results': None, 'error': None, 'domain': domain}
    
    # Launch background thread so Flask isn't blocked
    thread = threading.Thread(target=run_analysis_worker, args=(domain, lang_input.lower(), task_id))
    thread.start()
    
    return jsonify({"task_id": task_id})

@app.route("/status/<task_id>")
def get_status(task_id):
    """Frontend polls this route for live updates."""
    task = TASKS.get(task_id, {})
    return jsonify({
        "status": task.get("status", "Processing..."),
        "complete": task.get("complete", False)
    })

@app.route("/result/<task_id>")
def show_result(task_id):
    """Renders the final page once the background thread finishes."""
    task = TASKS.get(task_id)
    if not task:
        return render_template("index.html", error="Task not found or expired.")
        
    if task.get('error'):
        return render_template("index.html", error=task['error'])
        
    results = task.get('results')
    domain = task.get('domain')
    
    h_count, m_count, l_count = calculate_counts(results['highlights'], results['full_text'])
    risk_counts = {'High Risk': h_count, 'Medium Risk': m_count, 'Safe': l_count}
    dominant_risk = max(risk_counts, key=risk_counts.get)
    results['overall_risk'] = dominant_risk
    
    chart_base64 = create_pie_chart_base64(h_count, m_count, l_count)
    RESULT_CACHE[domain] = results
    
    # Clean up memory
    del TASKS[task_id]
    
    return render_template(
        "index.html", 
        results=results, domain=domain, dominant_risk=dominant_risk,
        chart=chart_base64, h_count=h_count, m_count=m_count
    )

@app.route("/download/<domain>")
def download_pdf(domain):
    results = RESULT_CACHE.get(domain)
    if not results:
        return "Report expired or not found", 404
    pdf_bytes = pdf_generator.create_report(results)
    return send_file(io.BytesIO(pdf_bytes), mimetype='application/pdf', as_attachment=True, download_name=f"Termsly_{domain}.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)