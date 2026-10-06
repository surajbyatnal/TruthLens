"""Step 1 - Big data processing with Pandas: load, clean, aggregate, analyze.
Reads  data/raw/Fake.csv and data/raw/True.csv   (columns: title, text, subject, date)
Writes data/processed/news_clean.csv and data/processed/analytics.json"""
import json, os, re
import pandas as pd

os.makedirs("data/processed", exist_ok=True)

# 1. LOAD
fake = pd.read_csv("data/raw/Fake.csv"); fake["label"] = "FAKE"
true = pd.read_csv("data/raw/True.csv"); true["label"] = "REAL"
df = pd.concat([fake, true], ignore_index=True)
raw = len(df)
print(f"[load]      {raw:,} raw records")

# 2. CLEAN
n0 = len(df)
df = df.dropna(subset=["title", "text"])
df = df[(df.title.str.strip() != "") & (df.text.str.strip() != "")]
nul = n0 - len(df)

n0 = len(df)
df = df.drop_duplicates(subset=["title", "text"])
dup = n0 - len(df)

df["text"] = df.text.str.replace(r"^.*?\(Reuters\)\s*-\s*", "", regex=True)   # source tag leaks the label (ISOT)
df["text"] = df.text.str.replace(r"http\S+|www\.\S+", " ", regex=True)
df["words"] = df.text.str.split().str.len()
n0 = len(df)
df = df[df.words >= 10]
short = n0 - len(df)

n0 = len(df)
df["date"] = pd.to_datetime(df.date, errors="coerce")
df = df.dropna(subset=["date"])
nul += n0 - len(df)
df["subject"] = df.subject.astype(str).str.strip()
print(f"[clean]     removed {dup:,} duplicates, {nul:,} missing/invalid rows, {short:,} very short articles -> {len(df):,} left")

# 3. AGGREGATE
by_cat = {}
for (subj, lab), n in df.groupby(["subject", "label"]).size().items():
    by_cat.setdefault(subj, {"fake": 0, "real": 0})[lab.lower()] = int(n)
monthly = df.groupby([df.date.dt.to_period("M").astype(str), "label"]).size().unstack(fill_value=0)
monthly = monthly.reindex(columns=["FAKE", "REAL"], fill_value=0)
print("[aggregate] categories:", len(by_cat), "| months:", len(monthly))

# 4. STATISTICAL ANALYSIS
df["excl"] = df.text.str.count("!")
df["caps"] = df.text.apply(lambda t: len(re.findall(r"\b[A-Z]{4,}\b", t)))
feat = []
for name, col in [("Words", "words"), ("Exclamation marks", "excl"), ("ALL-CAPS words", "caps")]:
    for lab in ["FAKE", "REAL"]:
        s = df.loc[df.label == lab, col]
        feat.append(dict(name=name, cls=lab.lower(), mean=float(s.mean()), median=float(s.median()), std=float(s.std())))
        print(f"[stats]     {name:<18} {lab}: mean={s.mean():.1f} median={s.median():.0f} std={s.std():.1f}")

analytics = dict(
    raw=int(raw), dup=int(dup), nul=int(nul), short=int(short), total=int(len(df)),
    fake=int((df.label == "FAKE").sum()), real=int((df.label == "REAL").sum()),
    byCat=by_cat,
    trend=dict(labels=list(monthly.index), fake=[int(x) for x in monthly.FAKE], real=[int(x) for x in monthly.REAL],
               sub="Monthly article counts across the whole dataset"),
    avgWords=dict(fake=float(df[df.label == "FAKE"].words.mean()), real=float(df[df.label == "REAL"].words.mean())),
    featStats=feat,
)
json.dump(analytics, open("data/processed/analytics.json", "w"))
df[["title", "text", "subject", "date", "label", "words"]].to_csv("data/processed/news_clean.csv", index=False)
print("[done]      wrote data/processed/news_clean.csv and analytics.json")
