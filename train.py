"""Step 2 - Train the classifier (TF-IDF + Logistic Regression) and save model + metrics."""
import json, os, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

os.makedirs("model", exist_ok=True)
df = pd.read_csv("data/processed/news_clean.csv")
X = df.title + ". " + df.text
y = (df.label == "FAKE").astype(int)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

pipe = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english", max_features=50000, ngram_range=(1, 2), min_df=3)),
    ("clf", LogisticRegression(max_iter=1000)),
])
pipe.fit(Xtr, ytr)
pred = pipe.predict(Xte)
tn, fp, fn, tp = confusion_matrix(yte, pred).ravel()
acc, prec, rec, f1 = accuracy_score(yte, pred), precision_score(yte, pred), recall_score(yte, pred), f1_score(yte, pred)
print(f"train={len(Xtr):,} test={len(Xte):,}")
print(f"accuracy={acc:.4f} precision={prec:.4f} recall={rec:.4f} f1={f1:.4f}")
print(f"confusion matrix: TP={tp} FN={fn} FP={fp} TN={tn}")

joblib.dump(pipe, "model/model.pkl")
a = json.load(open("data/processed/analytics.json"))
a.update(acc=acc * 100, prec=prec, rec=rec, f1=f1, cm=dict(tp=int(tp), fn=int(fn), fp=int(fp), tn=int(tn)), testN=int(len(yte)))
json.dump(a, open("data/processed/analytics.json", "w"))
print("saved model/model.pkl and updated analytics.json")
