"""Generates a SYNTHETIC fake/real news dataset in the same format as the Kaggle ISOT files
(Fake.csv and True.csv with columns: title, text, subject, date).

This is demo data so the whole project runs out of the box. It is NOT real news.
For real results, download the Kaggle "Fake and Real News Dataset" and replace
data/raw/Fake.csv and data/raw/True.csv (see README.md)."""
import csv, random, datetime, os

random.seed(42)
N_FAKE, N_REAL = 3200, 3000

REAL_EVENTS = {
 "Politics": ["approved a revised budget for regional road repairs", "passed a bill on public school funding", "announced new rules for campaign finance reporting", "confirmed the date of the next municipal election", "extended the review period for a proposed housing law"],
 "Health": ["reported a decline in seasonal flu cases", "opened a new outpatient clinic in the northern district", "published updated vaccination guidelines for children", "expanded screening for high blood pressure", "released results of a nationwide nutrition survey"],
 "Technology": ["launched a pilot of electric buses on three routes", "published a study on energy-efficient chips", "rolled out a security update for its payment app", "opened a new data centre outside the capital", "announced a partnership to expand rural broadband"],
 "Sports": ["won the league opener with a late goal", "named its squad for the upcoming qualifiers", "confirmed the venue for the national championship", "signed a two-year deal with its head coach", "reported record attendance for the season"],
 "Business": ["reported a narrower quarterly loss", "said retail sales rose in the third quarter", "announced plans to open 20 new stores", "raised its full-year profit forecast", "agreed to acquire a regional logistics firm"],
 "Entertainment": ["announced the lineup for its annual film festival", "confirmed a new season of its drama series", "opened a retrospective of regional photography", "released its summer concert schedule", "named the jury for this year's awards"],
 "Science": ["confirmed the launch window for its lunar orbiter", "published findings on coral recovery at a monitored reef", "released new satellite data on glacier retreat", "began a three-year study of soil health", "announced funding for a deep-sea survey"],
 "World": ["agreed to extend a regional trade pact for five years", "delivered relief supplies to flood-hit districts", "signed a joint statement on border cooperation", "opened talks on a shared water agreement", "announced a donor conference for reconstruction"],
}
FAKE_CLAIMS = {
 "Politics": ["the election results were secretly changed by hidden officials", "a minister is hiding millions in a secret account", "the government plans to cancel the next vote", "leaders signed a secret deal to give away the country"],
 "Health": ["a miracle fruit cures every disease in three days", "doctors are hiding a one weird trick that melts belly fat", "vaccines contain secret microchips", "drinking hot water cures cancer overnight"],
 "Technology": ["your phone is secretly recording your thoughts at night", "a free iPhone giveaway ends tonight", "a hidden app is stealing your bank balance", "every smart TV is spying on your family"],
 "Sports": ["the star player secretly bribed the referee", "the league is rigging the final for money", "a coach was caught in a mysterious scandal", "the team will be banned overnight"],
 "Business": ["banks will collapse tomorrow and take your savings", "a banned trick makes anyone rich in 24 hours", "the government will ban cash overnight", "a millionaire exposed the secret of free money"],
 "Entertainment": ["the famous actor is dead in a mysterious accident", "the singer's secret marriage was just exposed", "a star was caught in a shocking scandal", "a hidden video shows the truth about the festival"],
 "Science": ["scientists confirm the moon is hollow and full of aliens", "a hidden city was found under the ice", "a secret experiment created a miracle energy source", "the space agency is covering up a bombshell discovery"],
 "World": ["authorities silenced witnesses to a hidden city under the ice", "leaders plan to ban all travel overnight", "a leaked memo reveals the secret plan for a new world order", "the mainstream media is covering up a massive scandal"],
}
ORGS = ["The ministry", "The city council", "The statistics office", "The national federation", "The regional commission", "The university", "The transport authority", "The company", "The agency", "The health department"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DOCS = ["report", "statement", "survey", "filing", "study"]
WHEN = ["on Friday", "last week", "earlier this month", "on Tuesday"]
NAMES = ["Maria Lopez", "Arun Mehta", "John Carter", "Li Wei", "Fatima Khan", "Peter Novak", "Sara Ahmed", "David Okafor"]
STEPS = ["approval by the full committee", "a final vote next month", "review by an independent panel", "ratification by regional authorities"]
HEADS = ["SHOCKING", "BREAKING", "UNBELIEVABLE", "BOMBSHELL", "EXPOSED", "WAKE UP", "MIND-BLOWING"]
ANON = ["Anonymous insiders", "Unnamed experts", "A secret whistleblower", "Hidden sources"]

def real_article(subj):
    org, ev = random.choice(ORGS), random.choice(REAL_EVENTS[subj])
    n = random.choice([3, 4, 5, 6, 8, 12, 18, 25, 40])
    s = [f"{org} said on {random.choice(DAYS)} that it {ev}."]
    pool = [
        f"According to a {random.choice(DOCS)} published {random.choice(WHEN)}, the change affects about {random.randint(2,95)*100} people.",
        f"{random.choice(NAMES)}, a spokesperson for the organisation, told reporters that the decision followed several months of review.",
        f"Analysts surveyed before the announcement had expected a change of about {n} percent.",
        f"The measure still requires {random.choice(STEPS)}, officials said.",
        f"The figures, which cover {random.randint(120,900)} sites, will be updated in the next quarterly report.",
        f"Opposition members said they would examine the details before commenting.",
        f"A statement on the official website said further data would be released in {random.choice(['March','June','September','December'])}.",
        f"Researchers at a local university cautioned that the results are preliminary and need further validation.",
    ]
    s += random.sample(pool, random.randint(3, 6))
    title = f"{org.replace('The ', '').capitalize()} {ev}"
    if random.random() < 0.1:   # hard case: real article quoting an unnamed source
        s.insert(2, "A source familiar with the matter said more details would follow, but the claim could not be independently confirmed.")
    if random.random() < 0.08:   # hard case: real article with emotional wording
        s.insert(2, f"Residents were shocked, the {org.lower().replace('the ','')} said, calling the situation unbelievable!")
    return title, " ".join(s)

def fake_article(subj):
    claim = random.choice(FAKE_CLAIMS[subj])
    if random.random() < 0.15:   # hard case: fake claim written in the calm style of real reporting
        org = random.choice(ORGS)
        title = f"{org.replace('The ', '').capitalize()} says {claim}"
        text = (f"{org} said on {random.choice(DAYS)} that {claim}. "
                f"According to a {random.choice(DOCS)} published {random.choice(WHEN)}, the change affects about {random.randint(2,95)*100} people. "
                f"{random.choice(NAMES)}, a spokesperson for the organisation, told reporters that the decision followed several months of review. "
                f"The measure still requires {random.choice(STEPS)}, officials said.")
        return title, text
    title = f"{random.choice(HEADS)}: {claim.capitalize()}{'!' * random.choice([0, 1, 3])}"
    bank = [
        f"You won't believe what {random.choice(ANON).lower()} just revealed: {claim}!",
        f"{random.choice(ANON)} say the truth is being hidden from you.",
        "Share this before it gets deleted!!!",
        f"The mainstream media refuses to cover the story that {claim}.",
        f"WAKE UP people, {claim.upper()}.",
        "Click here now to see the shocking proof they tried to ban.",
        "Insiders claim a massive cover-up is underway and nobody will talk about it.",
        "Millions are stunned and the elites are panicking.",
        "Only a few hours left before this secret is censored.",
    ]
    return title, " ".join(random.sample(bank, random.randint(3, 6)))

def rand_date():
    start = datetime.date(2024, 1, 1); span = (datetime.date(2026, 9, 30) - start).days
    return (start + datetime.timedelta(days=random.randint(0, span))).isoformat()

def write(path, n, maker):
    subjects = list(REAL_EVENTS)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["title", "text", "subject", "date"])
        for _ in range(n):
            subj = random.choice(subjects); t, x = maker(subj); w.writerow([t, x, subj, rand_date()])
        # inject a few messy rows so the cleaning step has something to do
        for _ in range(40): w.writerow(["", "", "Politics", rand_date()])
        for _ in range(60): w.writerow(["Short note", "Too short.", "World", rand_date()])

os.makedirs("data/raw", exist_ok=True)
write("data/raw/Fake.csv", N_FAKE, fake_article)
write("data/raw/True.csv", N_REAL, real_article)
print("Wrote data/raw/Fake.csv and data/raw/True.csv (synthetic demo data)")
