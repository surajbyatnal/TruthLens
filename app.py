"""Step 3 - Flask backend: serves the web app, predicts with the trained model, stores history in SQLite."""
import json, os, re, sqlite3
from datetime import date

import joblib
from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="static", static_url_path="")
DB = "truthlens.db"

for f in ("model/model.pkl", "data/processed/analytics.json"):
    if not os.path.exists(f):
        raise SystemExit(f"Missing {f}. Run:  python prepare_data.py  then  python train.py")
pipe = joblib.load("model/model.pkl")
ANALYTICS = json.load(open("data/processed/analytics.json"))

CATS = {
    "Politics": "government minister election parliament president vote voter party bill senate policy opposition law court commission leaders",
    "Health": "health doctor doctors vaccine vaccines disease cure cures hospital hospitals flu cancer fat diet blood medical patients clinic",
    "Technology": "phone app chip chips software tech internet hack iphone processor electric digital data broadband",
    "Sports": "match team player league goal coach squad referee tournament qualifiers season championship",
    "Business": "bank banks market sales economy retail shares airline inflation rate money rich quarter trade millionaire cash profit",
    "Entertainment": "actor film films singer festival celebrity star movie music marriage director series concert awards",
    "Science": "scientists space moon lunar research researchers coral marine orbiter planet climate satellite",
    "World": "countries regional flood relief international border summit pact talks",
}
CAT_SETS = {k: set(v.split()) for k, v in CATS.items()}


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, text TEXT, label TEXT, confidence REAL,
        category TEXT, source TEXT, date TEXT, detail TEXT)""")
    con.commit()
    con.close()


def detect_category(text):
    words = re.findall(r"[a-z]+", text.lower())
    best, score = "General", 0
    for k, vocab in CAT_SETS.items():
        s = sum(1 for w in words if w in vocab)
        if s > score:
            best, score = k, s
    return best


def explain(text, k=8):
    """Words with the biggest push toward FAKE / REAL (TF-IDF weight x model coefficient)."""
    tf, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
    v = tf.transform([text])
    idx = v.nonzero()[1]
    if len(idx) == 0:
        return [], []
    names = tf.get_feature_names_out()
    contrib = v[0, idx].toarray()[0] * clf.coef_[0][idx]
    order = contrib.argsort()
    fake = [str(names[idx[i]]) for i in order[::-1][:k] if contrib[i] > 0]
    real = [str(names[idx[i]]) for i in order[:k] if contrib[i] < 0]
    return fake, real


def build_detail(text, label, fake_terms, real_terms):
    excl = text.count("!")
    caps = len(re.findall(r"\b[A-Z]{4,}\b", text))
    nums = len(re.findall(r"\b\d[\d,.]*\b", text))
    attributed = bool(re.search(r"according to|said|told|reported|announced", text, re.I))
    words = len(text.split())
    reasons = []
    if fake_terms:
        reasons.append("Words that push the model toward FAKE: " + ", ".join(f"“{w}”" for w in fake_terms[:4]) + ".")
    if real_terms:
        reasons.append("Words that push the model toward REAL: " + ", ".join(f"“{w}”" for w in real_terms[:4]) + ".")
    if excl >= 2 or caps >= 2:
        reasons.append(f"Emotional formatting: {excl} exclamation mark(s) and {caps} ALL-CAPS word(s).")
    if not attributed:
        reasons.append("No clear attribution to a named person, institution, or report.")
    if nums >= 2:
        reasons.append(f"Contains {nums} specific figures or dates, typical of verifiable reporting.")
    if words < 20:
        reasons.append("Very short text, so there is little verifiable detail.")
    summary = ("The vocabulary and style match patterns the model learned from misleading articles."
               if label == "FAKE" else
               "The vocabulary and style match patterns the model learned from conventional reporting.")
    return dict(reasons=reasons, summary=summary, suspicious=fake_terms, credible=real_terms)


def row_to_dict(r):
    d = dict(r)
    d["detail"] = json.loads(d.get("detail") or "{}")
    return d


@app.get("/")
def home():
    return app.send_static_file("index.html")


@app.post("/api/predict")
def predict():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    if len(text.split()) < 8:
        return jsonify(error="Add at least 8 words so the model has enough to analyze."), 400
    p_fake = float(pipe.predict_proba([text])[0][1])
    label = "FAKE" if p_fake >= 0.5 else "REAL"
    conf = round(max(p_fake, 1 - p_fake) * 100, 1)
    fake_terms, real_terms = explain(text)
    detail = build_detail(text, label, fake_terms, real_terms)
    title = (data.get("title") or text.split("\n")[0])[:90]
    con = db()
    cur = con.execute(
        "INSERT INTO history(title,text,label,confidence,category,source,date,detail) VALUES(?,?,?,?,?,?,?,?)",
        (title, text[:2000], label, conf, detect_category(text), (data.get("source") or "User submitted")[:80],
         date.today().isoformat(), json.dumps(detail)))
    con.commit()
    row = con.execute("SELECT * FROM history WHERE id=?", (cur.lastrowid,)).fetchone()
    con.close()
    return jsonify(row_to_dict(row))


@app.get("/api/history")
def history():
    con = db()
    rows = con.execute("SELECT * FROM history ORDER BY id DESC").fetchall()
    con.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.delete("/api/history")
def clear_history():
    con = db()
    con.execute("DELETE FROM history")
    con.commit()
    con.close()
    return jsonify(ok=True)


@app.get("/api/analytics")
def analytics():
    return jsonify(ANALYTICS)


if __name__ == "__main__":
    init_db()
    print("TruthLens running at http://127.0.0.1:5000")
    app.run(debug=False, port=5000)
