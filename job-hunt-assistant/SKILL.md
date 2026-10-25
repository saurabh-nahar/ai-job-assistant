---
name: job-hunt-assistant
description: Personal daily job hunt. Sets up a job seeker's profile through a short interview (resume, target roles, location, salary, deal-breakers), then each day finds fresh postings on LinkedIn (Apify), HiringCafe and Indeed, keeps only roles with a 60%+ shortlist chance, and builds a tailored PDF and Word resume plus recruiter, hiring-manager and referral messages for each. It also tracks applications and replies from Gmail in a Job Application Tracker. Use for "set up my job hunt", "run my job hunt", "update my job hunt profile", job links the user sends, interview guide requests and the weekly review.
---

# Job Hunt Assistant

This skill works for anyone. Nothing about the user is built in: everything personal lives in a
**profile** saved inside the user's own **Job Application Tracker** (a private claude.ai page with a
small database). The first run is a friendly setup interview that creates the profile and the
tracker. Every later run reads the profile and does the job hunt.

The scripts this skill uses are in its `scripts/` folder and the tracker page is `assets/tracker.html`.
Below, `<skill>` means this skill's base directory. Copy the scripts into the run's working
directory before using them.

## 0. Pick the mode

| The user says / the session is… | Mode |
|---|---|
| "set up my job hunt", or no profile exists yet | **Setup** (section 2) |
| "update my profile", "I'm now targeting…", "stop showing me…", a correction to a resume or message | **Update profile** (section 3) |
| "run my job hunt", "find jobs", a scheduled run | **Daily run** (sections 4–9) |
| one or more job links | **Job links** (section 10) |
| "interview guide for…", "I have an interview with…" | **Interview guide** (section 11) |
| the weekly scheduled review | **Weekly review** (section 12) |

Always start by **finding the tracker and profile** (section 1). If there is no profile and the
request isn't Setup, say in one line that setup comes first and start it. In a scheduled
(unattended) run with no profile, send nothing and stop: setup needs the person.

## 1. Find the tracker and profile

1. Load tools with one ToolSearch call: `select:ArtifactData,mcp__Gmail__search_threads,mcp__Gmail__get_thread,mcp__Gmail__send_message,mcp__HiringCafe_Job_Search__search_jobs,mcp__HiringCafe_Job_Search__get_job_details,mcp__Indeed__search_jobs,mcp__Indeed__get_job_details,mcp__apify__call-actor,mcp__apify__get-actor-run,mcp__apify__get-dataset-items`. Custom connectors are named by the user, so their tool prefix can differ (for example `mcp__Apify__` or `mcp__HiringCafe__`): for any tool the select didn't find, run ToolSearch by keyword (`apify call-actor`, `hiringcafe search_jobs`, `indeed search_jobs`) and use whatever comes back. Still missing means that connector isn't connected; that's fine (see "Sources").
2. `Artifact` with `action: "list"`, `limit: 50`. Find the artifact titled **Job Application Tracker**. If there are several, use the one whose database has `meta/profile` (try `ArtifactData` `get`, collection `meta`, doc `profile`).
3. Read `meta/profile` and save it locally: `ArtifactData` `get` with `out_dir: ./profile` → `./profile/meta/profile.json`. Scripts read this file.
4. Read `meta/patterns` and all `jobs` (`list`, `query.limit: 1000`, `out_dir` when there are many).

Remember the tracker URL for the rest of the run.

## 2. Setup interview (first run)

Goal: in about 10 minutes, collect everything the daily run needs, in plain language, one topic at
a time. Be warm and brief. Use `AskUserQuestion` for choices (2–4 options, the user can always type
their own), and plain chat for free text and file uploads. Never ask for passwords, ID numbers or
bank details. Tell the user at the start: *"I'll ask about 8 quick questions. You can say 'skip'
to anything and change it later."*

**Before asking anything, check connectors silently** (section 1, step 1) and tell the user in one
line which job sources are ready (LinkedIn via Apify, HiringCafe, Indeed, or another job-board
connector) and whether Gmail is connected. Outside Canada and the US, ask which job site people in
their country mostly use, and check `SearchMcpRegistry` for a connector for it; if one exists, suggest
connecting it with `SuggestConnectors`. If none of the three job sources is connected, say the daily run needs at least one and
point them to the setup guide, but carry on with the interview.

### Q1. Resume
Ask them to **attach their current resume** (PDF or Word) or paste it. Read it fully. Build the
**master resume** (schema in section 2.2) using only what the file says. Then show a short summary
back (current title, employers and dates, 3–5 strongest results) and ask:
- "Is all of this accurate?"
- "Any results with numbers that aren't on the resume? (growth %, money saved, team size, users…)"
- "Anything I should never claim?" (titles you didn't hold, tools you only watched others use)
Add confirmed extras to the master. Never invent or round numbers.

### Q2. Contact and sign-off
Confirm name, city, email, phone, LinkedIn URL (from the resume when present), the first name to sign
messages with, and **which email should get the daily digest**.

### Q3. Target roles
Propose 5–8 job titles that fit the resume (realistic now, not aspirational) and ask them to keep,
remove or add (`AskUserQuestion`, multi-select, then free text). Then ask:
- "Any titles or kinds of work you *don't* want, even if the title matches?" (e.g. sales-heavy, cold
  calling, people management, a specialty they're leaving)
- "One level up is a stretch you'd still like to see?" (yes/no)
- Their honest seniority: the most years of experience in this field they can credibly claim.

### Q4. Location
- Home city (and country). Commute limit: about 30 minutes / 1 hour / 2 hours.
- Remote: "remote anywhere in my country", "remote in my state/province only", or "no remote".
- Hybrid OK? Willing to relocate? (default no)

### Q5. Pay
Minimum acceptable salary per year and currency. Explain the rule in one line: *"Most postings don't
list pay, so a missing salary won't hide a job. If a posting lists a range that sits fully below your
minimum, I'll skip it."* Also: full-time only, or are contracts of 12+ months OK?

### Q6. Employers
- Preferred industries (offer 4 likely ones from the resume, multi-select, plus free text).
- Smallest company size they'd consider (10 / 15 / 50 / 200+ people).
- Any to avoid (staffing agencies, gambling, a past employer…).

### Q7. Deal-breakers and strengths
- Tools or platforms that postings in their field often *require* but they have never used. Propose a
  list from your knowledge of the field and let them tick (these become hard blockers when a posting
  makes them mandatory).
- Languages: which they speak; drop postings that *require* fluency in others (e.g. French in parts of
  Canada).
- What they're unusually strong in (2–5 things), from the resume; these earn the "differentiator"
  points.
- Career direction in a few words (e.g. "manager in 2 years, head of department later").

### Q8. Schedule
- Run time: weekdays or every day, and what time (default 8:30 am in their time zone).
- Ask permission to create two **scheduled tasks**: the daily run and a short weekly review on Sunday.

### 2.1 After the interview
1. Derive the **search setup** (section 2.3) and the **story bank** (5–10 STAR stories from the master,
   each with "use for" tags; never add facts).
2. **Create the tracker**: load the `artifact-capabilities` skill (required before passing
   capabilities), then publish `<skill>/assets/tracker.html` with the `Artifact` tool,
   `icon: "briefcase"`, `title: "Job Application Tracker"`,
   `capabilities: {"db": {}, "user": {}, "assets": {}, "downloads": true}`, and a one-line description.
3. Write the profile: `ArtifactData` `set` collection `meta`, doc `profile` (JSON from a local file via
   `file_path`). Also `set` `meta/patterns` to
   `{"active": [], "watching": [], "bands": [], "last_gmail_scan": "", "summary": "No replies yet. Patterns appear after a few weeks of applications."}`.
4. **Seed past applications (optional, ask first):** "Want me to look through your Gmail for jobs you
   already applied to in the last 60 days?" If yes, run the Gmail scan (section 8) with a 60-day window
   and add rows.
5. **Create the scheduled tasks** with the session's scheduling tool (`create_trigger`; ToolSearch for it
   if needed). Daily prompt: `Run my job hunt (job-hunt-assistant skill): daily run.` Weekly prompt:
   `Run the weekly review of my job hunt (job-hunt-assistant skill).` Use the user's time zone in
   `CRON_TZ=`. Tell them in one sentence which approval setting each task got, and that if the daily
   email doesn't arrive they should open the task and turn on **automatic approval**, because the run
   sends an email and saves files while nobody is watching.
6. Offer to **run the first search now**. Finish with a 3-line summary: what's saved, when it runs,
   where the tracker is ("the card above").

### 2.2 Profile schema (`meta/profile`)

```json
{
 "version": 1, "updated": "YYYY-MM-DD",
 "name": "", "first_name": "", "city": "", "country": "", "country_code": "US",
 "email": "", "phone": "", "linkedin": "", "digest_email": "", "timezone": "America/Chicago",
 "contact": ["City, Region, Country", "email", "phone", "linkedin.com/in/…"],
 "current_title": "the real title; never upgrade it",
 "master": {
   "summary": "", "headlines": ["positioning lines the user likes"],
   "experience": [{"title": "", "company": "", "location": "", "dates": "Mon YYYY – Mon YYYY", "bullets": [""]}],
   "skills": [{"label": "", "items": [""]}], "education": [""], "certifications": [""]
 },
 "never_claim": [""], "honest_gaps": [""], "corrections": [{"date": "", "rule": ""}],
 "targets": {"titles": [""], "stretch_ok": true, "avoid_titles": [""], "avoid_work": [""],
             "max_years_claimable": 3, "career_direction": ""},
 "location": {"home": "Chicago, IL", "region": "Illinois, United States", "commute": "1h",
              "nearby_cities": [""], "remote": "country|region|none", "hybrid_ok": true, "relocate": false},
 "pay": {"currency": "USD", "floor": 75000, "contracts_ok": "12m+"},
 "employers": {"preferred_industries": [""], "min_employees": 15, "avoid": ["staffing agencies"]},
 "blockers": {"tools_never_used": [""], "languages_spoken": ["English"]},
 "differentiators": [""],
 "stories": [{"id": "S1", "title": "", "s": "", "t": "", "a": "", "r": "", "use_for": [""]}],
 "schedule": {"days": "weekdays", "time": "08:30"},
 "sources": {"linkedin": true, "hiringcafe": true, "indeed": true, "apify_budget_usd": 1,
             "other": [{"name": "", "search_tool": "", "details_tool": ""}]},
 "search": {
   "linkedin_keywords": "\"marketing manager\" OR \"product marketing\" OR …",
   "linkedin_location": "Illinois, United States", "linkedin_remote_location": "United States",
   "hiringcafe_departments": ["Marketing"], "hiringcafe_city": "Chicago, IL", "hiringcafe_radius_miles": 50,
   "hiringcafe_titles": ["product marketing", "marketing manager"],
   "indeed_titles": [""], "indeed_cities": [""]
 }
}
```

### 2.3 Search setup (derived, shown to the user only if they ask)
- **LinkedIn boolean query:** the target titles (and short title stems, e.g. `"marketing"` covers most
  marketing titles) joined with `OR`, each in quotes. Location = home region; remote search = country.
- **HiringCafe departments:** pick from the connector's department list (Engineering, Software
  Development, Information Technology, Data and Analytics, Design, Creative and Art Services, Project and
  Program Management, Product Management, Business Operations, Legal and Compliance, Finance and
  Accounting, Human Resources, Administrative & Clerical Support, Sales, Marketing, Communications and
  Public Affairs, Business Development). Radius in miles from the commute answer (30 min ≈ 25, 1 h ≈ 50,
  2 h ≈ 90).
- **Indeed:** 6–10 target titles × home city, 2–4 nearby cities (rotated by day), and 2 remote searches.

## 3. Update profile

When the user changes a preference or corrects something ("never say I managed people", "the
revenue growth was 25% not 52%", "add product marketing roles", "raise my minimum to 90K"):
read `meta/profile`, change only what they said, add a dated entry to `corrections` for anything
about how resumes or messages are written, `update` the doc pinned to the version you read, and
confirm in one line. Corrections apply to every future resume and message.

## 4. Daily run: overview

1. Section 1 (tracker, profile, patterns, jobs). Today's date: `TZ=<profile.timezone> date +%F`.
   Work in `./jobhunt/<date>/`.
2. **Start the LinkedIn pull first** (if Apify is connected), then while it runs: Gmail scan (section 8),
   interview guides that are due (section 11), HiringCafe and Indeed searches.
3. Merge, filter, score (sections 5–6), keep 60%+ (max 10).
4. Build resumes and messages, review the strongest, publish the day's page, record in the tracker,
   email the digest (section 9).

The run is unattended: never ask questions. Make the reasonable call and say so on the page. If the
user asked for a wider window ("last 72 hours"), use it for every source and say so on the page.

**Sources** (use whichever are connected; at least one is needed):

**LinkedIn via Apify** (`curious_coder/linkedin-jobs-scraper`, one run, two search URLs, past 24 h):
```json
{"actor": "curious_coder/linkedin-jobs-scraper",
 "input": {"urls": [
   "https://www.linkedin.com/jobs/search/?keywords=<urlencoded linkedin_keywords>&location=<urlencoded linkedin_location>&f_TPR=r86400",
   "https://www.linkedin.com/jobs/search/?keywords=<same>&location=<urlencoded linkedin_remote_location>&f_TPR=r86400&f_WT=2"],
  "limitPerSource": 1000, "scrapeCompany": true, "autoConvertToAiSearch": false},
 "waitSecs": 45, "callOptions": {"maxTotalChargeUsd": <profile.sources.apify_budget_usd>}}
```
`autoConvertToAiSearch` must be false (the AI search loosens the filters). For 72 hours use
`f_TPR=r259200`. Poll `get-actor-run` until `SUCCEEDED`, then triage with `get-dataset-items`
(`clean: true`, `limit: 1000`, `fields: "id,title,companyName,location,postedAt,salary,seniorityLevel,industries,companyEmployeesCount,applicantsCount,jobPosterName,jobPosterTitle,jobPosterProfileUrl"`)
and read the shortlist one row at a time (`offset`, `limit: 1`, add `link,descriptionText`). If the
run fails for **billing or credit** ("remaining usage … isn't enough"), don't retry: say on the page
and in the email that the Apify free credit has run out and LinkedIn was skipped.

**HiringCafe** (`search_jobs`, at most 25 rows a call; run in parallel, `posted_within_days: 1`):
1. departments + `hiringcafe_city` + radius, `seniority_levels: ["Mid Level"]`
2. same with `["Entry Level", "Senior Level"]`
3. departments + home region, `employment_types: ["Full Time", "Contract"]`
4. `search: <main field word>`, `location: "remote"`, `company_hq_countries: [country]` (skip if remote is "none")
5–6. `search: <hiringcafe_titles[i]>`, city + radius
Then `get_job_details` on the shortlist. Rows have no employee count or poster; the `url` is the link
exactly as returned.

**Indeed** (`search_jobs`, `country_code`, `job_type: "fulltime"`, about 10 rows a call, **no date
filter**): the searches from 2.3, in parallel batches of 4. Drop rows whose "Posted on" is older than
3 days before reading details. Job IDs only work in the same run: call `get_job_details` right away.
Tracker key: `in-<company>-<title>` (lowercase, hyphens, max 80 chars).

**Other job boards (other countries).** HiringCafe and Indeed cover Canada and the US well, but other
countries have their own leading boards. If the user has connected another job-search connector
(check the tool list, and `SearchMcpRegistry` with keywords like `["jobs", "job search", "<country>"]`
during setup), add it to `profile.sources.other` as `{name, search_tool, details_tool}` and use it
like Indeed: search the target titles and cities, drop stale rows by their posted date, read details,
and key rows `ot-<board>-<company>-<title>`. If no connector exists for a board the user relies on,
say so; don't scrape sites the tools decline.

If a source fails, retry once, then continue with the others and say so. If all fail, email a
one-line digest saying so and stop.

## 5. Filters (drop if any fail)

| Filter | Rule (values come from the profile) |
|---|---|
| Freshness | Within the window (24 h; Indeed 3 days). |
| Location | Within the commute limit of `location.home`, or remote within the allowed area. Further away in the same region: keep, flag, −5 unless remote/hybrid is offered. Remote roles open only to other countries: drop. |
| Size | ≥ `employers.min_employees` (judge from the description when the count is missing). Drop staffing agencies posting for unnamed clients. |
| Pay | Drop only when a **listed** range sits fully below `pay.floor` (the top is under about 97% of the floor). Hourly × 1,950. Missing pay is fine, but drop roles that read clearly junior when pay is missing. |
| Type | Full-time, or contracts per `pay.contracts_ok`. No internships, part-time, volunteer. |
| Language | Drop when fluency in a language not in `blockers.languages_spoken` is **required** ("an asset" is fine). |
| Unwanted work | Drop titles in `targets.avoid_titles`, and postings whose core duties match `targets.avoid_work`. |
| Reachability | Drop when the posting requires clearly more years than `targets.max_years_claimable` + 3, frames the role as the org's top expert, or makes a tool in `blockers.tools_never_used` a hard requirement ("or similar", "an asset", "nice to have" are not hard). |
| Seen before | Skip roles already in the tracker (match key, and company + normalized title). |
| Score | ≥ 60 after scoring. |

Name every notable drop (8–12) in `filtered` with the specific reason.

## 6. Scoring (0–100)

| Part | Points | How |
|---|---|---|
| Must-have coverage | 35 | Share of the posting's *required* qualifications the master resume proves. |
| Experience bar | 20 | Asked ≤ claimable years: 20. 1–2 above: 13–15. 3 above: 6. More: drop. |
| Tools | 10 | Required tools the master shows. |
| Employer fit | 10 | Preferred industry and size: 10. Preferred industry, small (under 50): 7. Other: 5. Agency: 4. |
| Pay and location | 10 | Listed pay reaching the floor and within commute/remote: 10. Not listed: 6. Far without remote: −5. |
| Differentiators | 10 | The posting values something in `differentiators`. |
| Direction | 5 | Moves toward `targets.career_direction`. |

Badges: Strong 75+, Good 65–74, Worth a look 60–64. The score is the odds of being shortlisted, not
an offer. **Golden bonus:** +5 when a role matches an active rule in `meta/patterns.active` (section
12); record `base_score`, `golden_bonus`, `golden_reason`, `score`. Keep ≥ 60, rank, cap at 10.
**Never lower the bar or pad the list:** three real matches beat ten weak ones.

Tag each kept role with `title_family` (the closest of `profile.targets.titles`, else "Other"),
`seniority` (Specialist · Manager · Senior/Lead · Head of), `company_type` (B2B SaaS / software ·
Tech (other) · Finance / bank · Professional services · Logistics / supply chain · Manufacturing ·
Healthcare · Telecom · Real estate · Retail / consumer · Public sector / non-profit · Agency · Other)
and `company_size` (15–49 · 50–199 · 200–999 · 1,000+ · "").

## 7. What each kept role gets

### 7.1 Tailored resume (truthful)
- **Select, reorder and reword the master. Never invent** a claim, number, tool, employer, title or
  date. Use the posting's keywords only where the master backs them. Apply every `corrections` rule
  and never use anything in `never_claim`.
- Keep `current_title` exactly. Tailor the **headline** (≤ 95 characters).
- **Summary:** three plain sentences, 55–75 words, no "I": who they are, what they own, one proof
  point. Never mention the employer or "this role", no sales pitch, no long run-on lists.
- 1–3 bold keyword phrases per bullet with `**…**`, whole words only. Lead each job with the most
  relevant bullets; drop weak ones. Tools: 4–6 labelled lines. **Two pages maximum.**
- Write `<slug>.json` (schema in `scripts/render_resume.py`; `contact` from the profile) and run
  `python3 render_resume.py <slug>.json <Prefix>Resume_<slug>` where `<Prefix>` is the name with
  underscores (`Jane_Doe_`) and the slug is `Company_Role-Title`.
- **Number check:** `python3 number_check.py profile/meta/profile.json <Prefix>Resume_*.pdf`. Fix
  anything it flags and re-render.

### 7.2 Recruiter-eye review (75+ or golden, max 4 a run)
Get a fresh reader: spawn one `general-purpose` agent per role (in parallel) with only the posting
and the resume text (`pdftotext`), asking for JSON: must-haves covered/not covered, coverage %,
whether the top third keeps a recruiter reading, weak lines, missing keywords the resume already
backs, verdict (shortlist/maybe/pass) and one fix, and never to suggest adding experience. If the
Agent tool isn't available, do the review yourself in a separate pass that reads only those two
texts. Revise only in ways the master supports, re-render, re-check numbers, and record
`review: {coverage, notes}`.

### 7.3 Three people, two messages each
For the **recruiter**, **hiring manager** and an **internal referral**:
- `note`: LinkedIn connection request, **300 characters or fewer, counted**.
- `message`: the full message after they accept: recruiter and hiring manager **120–180 words**,
  referral **80–120 words**.
Rules: real first name when the posting names the person, else `[Name]`; plain, warm, professional,
no hype; only claims from the master; never claim work authorization, travel, languages or
clearances. If the posting raises those, leave `[confirm]`. Recruiter: fit with must-haves and that
they applied, ask to be put in front of the hiring manager. Hiring manager: 2–3 proof points tied to
the work, ask for 15 minutes. **Referral:** sound like a person, not a pitch: greeting, the role and
team, at most one plain fit clause ("It's close to what I do now."), the ask ("Would you be
comfortable referring me?"), "Happy to send my resume. Thanks!". No metrics or self-labels in the
note. The full referral message thanks them, gives the role and link, says the resume is attached,
offers to apply through their referral link, and gives an easy out. Sign with `first_name`. Add a
people-search link for each:
`https://www.linkedin.com/search/results/people/?keywords=<Company>%20<team or title>`.

### 7.4 Fit assessment
`scope`, `why` (2–3 specific lines tying resume facts to the posting), `thin` (one honest paragraph on
gaps), `angle` (the one thing to lead with).

## 8. Gmail tracking (read-only)

Every daily run, before the search. Never reply, label, archive or delete. Window: from
`meta/patterns.last_gmail_scan` minus one day (max 14 days; 30 in the weekly review; 60 at setup).
Searches (`search_threads`, `pageSize: 50`, `<D>` = days):
1. `from:(ashbyhq.com OR lever.co OR greenhouse.io OR greenhouse-mail.io OR myworkday.com OR workday.com OR bamboohr.com OR smartrecruiters.com OR icims.com OR adp.com OR employmenthero.com OR jobvite.com OR workable.com OR taleo.net OR successfactors.com OR breezy.hr OR recruitee.com OR teamtailor.com OR pinpointhq.com OR dayforcehcm.com OR ultipro.com OR rippling.com OR applytojob.com OR jazzhr.com) newer_than:<D>d`
2. `subject:(application OR applying OR applied OR candidacy OR interview OR "pre-screen" OR screening OR assessment OR offer OR "next steps") newer_than:<D>d -from:(linkedin.com OR indeed.com OR glassdoor.com OR ziprecruiter.com) -subject:"Job Matches" -in:sent`
3. `(from:linkedin.com subject:("application was sent" OR "your application")) OR (from:indeed.com subject:("application submitted" OR "your application")) newer_than:<D>d`
4. `in:sent newer_than:<D>d -to:<profile.email>` (threads where they wrote to a company)
5. `(interview OR "phone screen" OR calendly OR availability) newer_than:<D>d category:primary -in:sent`

Skip job alerts, newsletters and account mail. Read a thread (`get_thread`, `PLAIN_TEXT`) when the
preview is unclear. Classify: `applied` (received/thank you for applying), `rejected` (not moving
forward, another candidate, position filled), `interview` (invitation to talk, scheduling link,
availability request), `assessment` (test or case study), `replied` (a person writes without
scheduling), `offer`. Match to a row by company (+ title when named); confirmations without a title
match on company only when there's exactly one recent row. Unmatched applications get a
`gm-<thread id>` row. Update `replies`, `gmail_threads`, `status`, `status_date`, `stage_reached`
(furthest positive stage, never goes down), `first_reply`. Rows still `applied` after 21 days with
nothing back become `no_response`. Set `meta/patterns.last_gmail_scan` to today. A new interview or
assessment triggers an interview guide.

## 9. Build, publish, record, email

1. Copy `scripts/*` into the run directory. Render resumes, check numbers, run reviews (section 7).
2. Write `run.json` and run `python3 build_page.py .` (schema below). Fix anything it flags (a note
   over 300 characters, a message outside its word range) and rebuild.
3. Load the `artifact-capabilities` skill, then publish `job-matches-<date>.html` with the `Artifact`
   tool: `icon: "briefcase"`, `capabilities: {"downloads": true}`, a one-sentence description.
4. Upload each kept role's **resume PDF** to the tracker's assets (`Artifact` publish, `url` = tracker,
   `asset: true`, `file_paths` up to 25; the asset store doesn't take .docx, which stay on the day's
   page). Write one row per kept role with `ArtifactData` `batch` (`set`, no `if_version`): status
   `found`, `scraped` today, the scores and tags, `company_meta`, `scope`, `angle`, `thin`, `review`,
   `tools`, `jd` (trimmed to 20,000 characters), `resume_pdf` (asset URL), `daily_page`, empty
   `applied`, `stage_reached: "none"`, empty `replies` and `gmail_threads`, `outreach_sent: false`,
   `guide_requested: false`, `notes: ""`. Never overwrite the user's fields (`outreach_sent`,
   `guide_requested`, `notes`) on existing rows.
5. Email `profile.digest_email` with `send_message`. Subject:
   `Job Matches — {Mon D} — {N} roles ({top}% best)` or `Job Matches — {Mon D} — no roles cleared 60%`.
   HTML body: one line per role (score, linked title, company, location, salary, source), a prominent
   link to the day's page ("resumes and messages are here"), the filtered count, a short **"Your
   applications"** block (new replies, interviews, rejections, roles waiting 7–14 days) when there is
   anything, and the tracker link. Plain-text fallback. No attachments.
6. In a chat (not scheduled), also send the .docx resumes with SendUserFile. Final reply: the ranked
   list in a few lines plus anything unusual (failed source, empty day, new interview).

**run.json**
```json
{"date": "YYYY-MM-DD", "date_label": "Monday, March 2, 2026", "file_prefix": "Jane_Doe_",
 "tracker_url": "…", "eyebrow": "Daily job matches · LinkedIn · HiringCafe · Indeed",
 "stats": {"searches": 0, "pooled": 0, "reviewed": 0, "passed": 0, "note": "one sentence, with the split by source"},
 "jobs": [{"key": "li-123 | hc-abc | in-company-title", "slug": "Company_Role-Title",
   "title": "", "company": "", "location": "", "workmode": "", "url": "", "salary": "", "posted": "",
   "applicants": "", "company_meta": "Industry · size · via Source", "base_score": 0, "golden_bonus": 0,
   "score": 0, "golden_reason": "", "review": {"coverage": 0, "notes": ""}, "scope": "", "why": [""],
   "thin": "", "angle": "", "people": {"recruiter": "", "hiring_manager": "", "referral": ""},
   "search_rec": "", "search_hm": "", "search_ref": "",
   "messages": {"recruiter": {"note": "", "message": ""}, "hiring_manager": {"note": "", "message": ""},
                "referral": {"note": "", "message": ""}}}],
 "filtered": [{"role": "Title – Company (City)", "reason": ""}]}
```
`review` only when a review ran. Optional: `title`, `file_slug`, `filtered_title`, `stats.items`
(list of `[number, label]`), per-message `note_label` / `message_label`.

## 10. Job links on demand

The user pastes links and wants a score, resume and messages.
- **HiringCafe** (`hiringcafe.com/job/<slug>`): the last part of the slug is the Job ID →
  `get_job_details`.
- **LinkedIn** (`/jobs/view/<id>`, any URL with `currentJobId=<id>`, `lnkd.in`): fetch
  `https://www.linkedin.com/jobs/view/<id>` with Apify `apify--web-fetch` (`formats: ["text"]`), read
  down to the "Industries" block only. Fallback: the built-in browser, then Claude in Chrome (read
  only, never click Apply/Message/Connect), then ask them to paste the description.
- **Indeed** links: web-fetch or browser; else search the connector for the title and company.
Score honestly with the same rubric but **don't drop** the user's own picks: failed filters become
flags at the top of the assessment. If a gap makes applying pointless (a required language they
don't speak), say so and ask before building. Build and publish as in section 9 (page title
`Your Picks · {Mon D}`, `file_slug: picks-YYYY-MM-DD`), add the rows with `source: "Sent link"`, send
the files in chat, and don't email unless asked. If they mention someone they know at the company,
write the referral message to that person in a tone that fits the relationship.

## 11. Interview guides

Make one when Gmail shows a new interview or assessment, when a tracker row has `guide_requested`
true and no `guide_pdf`, or when the user asks. Steps: get the row's `jd` (refetch if empty); 2–4
`WebSearch` calls on the company (what it sells, size, news from the last 6 months, the
interviewer's role), each snapshot line ending with its source; write the guide JSON
(`scripts/render_guide.py`) using only the profile's master and stories: a 60-second pitch (130–160
words), why them, stories to have ready, 8–10 behavioural questions with STAR answers (for "a
failure" write `[Your own example]`, never invent one), 3–4 role questions, honest answers for gaps,
a 30-60-90 outline, 5 questions to ask, and logistics (salary: write "[confirm your number]").
Render, then `python3 number_check.py profile/meta/profile.json --guide <slug>_guide.json Interview_Guide_<slug>.pdf`.
Upload the PDF to the tracker assets, set `guide_pdf`, `guide_made`, `guide_requested: false`, and
mention it in the email (or send it in chat).

## 12. Weekly review (Sundays)

Run the Gmail scan with a 30-day window and the 21-day rule. Over rows with an `applied` date,
positive = `stage_reached` other than `none`; compute applications (n), positive (p), rate and lift
(rate ÷ overall rate) for each value of `title_family`, `seniority`, `company_type`, `company_size`,
`source`, location type and `outreach_sent`, plus reply rate by score band (60–64, 65–74, 75+).
**Active (golden) rules:** p ≥ 3, n ≥ 5, lift ≥ 2.0 (max 5). **Watching:** p ≥ 2, or p = 1 with n ≤ 3.
Drop an active rule whose lift falls below 1.5. With fewer than 2 positive replies overall, no rules
yet. Write `meta/patterns` (`summary` in 2–3 plain sentences, `overall`, `active`, `watching`,
`bands`, `updated`, `last_gmail_scan`) and email a short review: what's working, rules added or
dropped, this week's replies, applications waiting 7+ days, and the tracker link.

## 13. Changing how the skill works

Users will want to adjust things: message tone, resume style, scoring, which roles show up.
- **Personal preferences and facts** (their tone, a number, a title to avoid): save them in the profile
  (section 3). That is enough for most requests and takes effect on the next run.
- **Changes to the method itself** (a new section in every resume, a different message structure, a
  new source, a changed filter): read this SKILL.md, make the change, and offer the complete updated
  skill with the `propose_skills` tool (`kind: "improvement"`, `target: "job-hunt-assistant"`, the
  **whole** SKILL.md, not just the changed part) so the user can review and save it from the card. If
  that tool isn't available, give them the updated SKILL.md as a file and tell them to replace it in
  Settings → Capabilities → Skills. Explain the change in one or two plain sentences.

## 14. Troubleshooting (say these plainly to the user)

- **"Remaining usage … isn't enough"** from Apify: the free $5 monthly Apify credit is used up (a daily
  LinkedIn pull costs roughly $0.20–1.00, so the free credit lasts about one to three weeks). LinkedIn
  is skipped until the credit renews or they move to a paid Apify plan. The other sources still run.
  Don't suggest opening extra free accounts: Apify's terms allow one personal account per person.
- **A connector's tools are missing:** it isn't connected or is turned off. Point them to the setup
  guide's connector step.
- **No daily email:** the scheduled task is probably waiting for approval. Open the task and turn on
  automatic approval.
- **Nothing cleared 60%:** normal on quiet days and weekends. The page still lists near-misses. If it
  happens all week, offer to review the target titles and filters.
