# BOT V2 - Job Finder by Lucie
# Clean version
import requests
from bs4 import BeautifulSoup
import imaplib
import email
from email.header import decode_header

# =========================
# SETTINGS
# =========================
TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
EMAIL_USER = "YOUR_EMAIL"
EMAIL_PASS = "YOUR_APP_PASSWORD"

HEADERS = {"User-Agent": "Mozilla/5.0"}

KEYWORDS = [
    "data analyst",
    "business analyst",
    "business intelligence",
    "bi analyst",
    "bi developer",
    "power bi",
    "sql",
    "python",
    "excel",
    "dashboard",
    "reporting analyst",
    "data visualization",
    "analyst",
    "intern",
    "entry level",
    "consultant",
    "remote",
    "junior"
]

# =========================
# HELPERS
# =========================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)


def clean_subject(subject):
    decoded, encoding = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8")
    return decoded


def match_keywords(text):
    text = text.lower()
    return any(word in text for word in KEYWORDS)


# =========================
# GMAIL SECTION
# =========================
def get_gmail_jobs():
    results = []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        searches = [
            ('FROM "linkedin"', "LinkedIn"),
            ('FROM "wellfound"', "Wellfound"),
            ('FROM "freelancer"', "Freelancer")
        ]

        for search_query, source in searches:
            status, messages = mail.search(None, search_query)
            ids = messages[0].split()[-10:]

            for num in reversed(ids):
                _, msg_data = mail.fetch(num, "(RFC822)")

                for response in msg_data:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        subject = clean_subject(msg["Subject"])

                        if match_keywords(subject):
                            results.append(f"📩 {source}: {subject}")

        mail.logout()

    except Exception as e:
        results.append(f"⚠️ Gmail error: {e}")

    return results[:5]


# =========================
# REMOTEOK
# =========================
def get_remoteok_jobs():
    jobs = []

    try:
        url = "https://remoteok.com"
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        used = set()

        for link in soup.find_all("a", href=True):
            title = link.get_text(" ", strip=True)
            href = link["href"]

            if not href.startswith("/"):
                continue

            # Jen skutečné job URL
            if "/remote-" not in href and "/l/" not in href:
                continue

            # Vyřadit nesmysly
            bad_words = ["sign-up", "workers", "hire", "login"]
            if any(bad in href.lower() for bad in bad_words):
                continue

            full_link = "https://remoteok.com" + href

            if full_link in used:
                continue

            job_words = ["analyst", "developer", "engineer", "specialist", "consultant"]

            if match_keywords(title) and any(word in title.lower() for word in job_words):
                used.add(full_link)
                jobs.append(f"🌍 {title[:70]}\n{full_link}")

            if len(jobs) == 3:
                break

    except:
        jobs.append("⚠️ RemoteOK error")

    return jobs


# =========================
# FREELANCER WEB
# =========================
def get_freelancer_jobs():
    jobs = []

    try:
        url = "https://www.freelancer.com/jobs/data-analytics/"
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        used = set()

        for link in soup.find_all("a", href=True):
            title = link.get_text(" ", strip=True)
            href = link["href"]

            if "/projects/" not in href:
                continue

            if href.startswith("/"):
                full_link = "https://www.freelancer.com" + href
            else:
                full_link = href

            if full_link in used:
                continue

            if match_keywords(title):
                used.add(full_link)
                jobs.append(f"💸 {title[:70]}\n{full_link}")

            if len(jobs) == 3:
                break

    except:
        jobs.append("⚠️ Freelancer error")

    return jobs


# =========================
# MAIN REPORT
# =========================
def build_report():
    text = "☀️ Dobré ráno Lucie!\n"
    text += "━━━━━━━━━━━━━━\n"
    text += "🎯 Denní přehled příležitostí\n\n"

    gmail_jobs = get_gmail_jobs()
    if gmail_jobs:
        text += "📩 Gmail nabídky:\n"
        text += "\n".join(gmail_jobs)
        text += "\n\n"

    remote_jobs = get_remoteok_jobs()
    if remote_jobs:
        text += "🌍 Remote práce:\n"
        text += "\n\n".join(remote_jobs)
        text += "\n\n"

    freelancer_jobs = get_freelancer_jobs()
    if freelancer_jobs:
        text += "💸 Freelancer:\n"
        text += "\n\n".join(freelancer_jobs)

    return text


# =========================
# RUN
# =========================
if __name__ == "__main__":
    report = build_report()
    send_telegram(report)
    print("Hotovo ✅")