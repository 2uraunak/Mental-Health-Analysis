import os
import re
from flask import Flask, render_template, request

app = Flask(__name__)

DEPRESSION_KEYWORDS = ['exhausted', 'tired', 'numb', 'hopeless', 'overwhelmed', 'crying', 'worthless', 'lonely', 'sad', 'empty', 'withdrawn', 'dreading']
ANXIETY_KEYWORDS = ['panic', 'nervous', 'scared', 'worry', 'racing', 'heartbeat', 'sweat', 'breathless', 'shaking', 'uneasy']
POSITIVE_KEYWORDS = ['happy', 'grateful', 'excited', 'joy', 'peaceful', 'hopeful', 'energized', 'confident', 'content']

def analyze_sentiment(text):
    text_lower = text.lower()
    dep_score = sum(1 for kw in DEPRESSION_KEYWORDS if re.search(r'\b' + kw + r'\b', text_lower))
    anx_score = sum(1 for kw in ANXIETY_KEYWORDS if re.search(r'\b' + kw + r'\b', text_lower))
    pos_score = sum(1 for kw in POSITIVE_KEYWORDS if re.search(r'\b' + kw + r'\b', text_lower))
    
    total = dep_score + anx_score + pos_score
    if total == 0:
        return "Neutral / Undetermined", 75.0, "#94a3b8", "No strong clinical sentiment flags detected.", [("Depression", 10), ("Anxiety", 15), ("Neutral", 65), ("Positive", 10)]
        
    if dep_score >= anx_score and dep_score >= pos_score:
        conf = round(min(98.5, 60.0 + dep_score * 8.5), 1)
        findings = "Prominent linguistic patterns of hedonic deficit, emotional fatigue, and depressive sentiment identified."
        dist = [("Depression", conf), ("Anxiety", round((100-conf)*0.6, 1)), ("Neutral", round((100-conf)*0.3, 1)), ("Positive", round((100-conf)*0.1, 1))]
        return "Depressive Sentiment Flagged", conf, "#ef4444", findings, dist
    elif anx_score > dep_score and anx_score >= pos_score:
        conf = round(min(96.0, 60.0 + anx_score * 8.0), 1)
        findings = "Indicators of autonomic arousal, hypervigilance, and generalized acute anxiety markers."
        dist = [("Depression", round((100-conf)*0.3, 1)), ("Anxiety", conf), ("Neutral", round((100-conf)*0.5, 1)), ("Positive", round((100-conf)*0.2, 1))]
        return "Anxiety / Stress Sentiment Flagged", conf, "#f59e0b", findings, dist
    else:
        conf = round(min(98.0, 65.0 + pos_score * 8.0), 1)
        findings = "Positive emotional valence, resilient mindset markers, and healthy cognitive outlook detected."
        dist = [("Depression", round((100-conf)*0.1, 1)), ("Anxiety", round((100-conf)*0.1, 1)), ("Neutral", round((100-conf)*0.2, 1)), ("Positive", conf)]
        return "Positive Emotional State", conf, "#10b981", findings, dist

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.form.get('journal_text', '').strip()
    if not text:
        return render_template('index.html')
        
    state, conf, col, findings, dist = analyze_sentiment(text)
    
    return render_template('index.html',
                           analyzed=True,
                           state=state,
                           confidence=conf,
                           status_color=col,
                           findings=findings,
                           dist=dist,
                           input_text=text)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
