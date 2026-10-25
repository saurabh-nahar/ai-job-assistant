# Job Hunt Assistant: Setup Guide

## What this does

Every morning, Claude looks for new jobs that fit you, keeps only the ones where you have a real chance (60% or better), and gets everything ready so you can apply in minutes. Setup takes about 30 minutes, once.

For each good job you get:

- **An honest note:** why you fit, what's missing, and what to mention first.
- **Your resume, rewritten for that job,** as a PDF and a Word file. It only uses facts from your real resume.
- **Ready-to-send LinkedIn messages for three people:** the recruiter, the hiring manager, and someone on the team who could refer you. Each gets a short connection note and a longer follow-up message.

You also get:

- **A Job Application Tracker** page that lists every job and notices when companies email you back (thank you, interview, rejection).
- **A short email each morning** with links to everything.
- **Interview prep notes** when a company invites you to an interview.

## Before you start

Tick these off before Step 1:

- [ ] A paid Claude plan (Pro, Max, Team or Enterprise). Skills and scheduled runs aren't on the free plan.
- [ ] A computer with a web browser. Setup doesn't work from the phone app, but you can read your results on your phone later.
- [ ] Your current resume as a PDF or Word file.
- [ ] A Gmail account, for the daily email and for tracking replies from companies.
- [ ] The skill file **job-hunt-assistant.zip**. Download it from this project's [Releases page](../../releases/latest). Keep it zipped.
- [ ] Optional: a free Apify account, if you want LinkedIn jobs (Step 3).

## Step 1: Turn on file creation and skills

This lets Claude make resume files and use the job hunt skill.

1. Go to **claude.ai** and sign in.
2. Click your name or initials (bottom left), then **Settings**.
3. Open **Capabilities**.
4. Turn on **Code execution and file creation**.
5. Scroll down to **Skills** and make sure skills are turned on.

On a Team or Enterprise plan, your admin may need to turn these on first. ([Claude help: using skills](https://support.claude.com/en/articles/12512180-using-skills-in-claude))

## Step 2: Connect Gmail

Claude uses Gmail to send you the morning summary and to notice replies from companies.

1. Start a new chat in Claude.
2. Click the **+** button at the bottom left of the message box.
3. Hover over **Connectors** and turn **Gmail** on.
4. When Google asks, sign in and allow access.

Claude only reads job-related emails, and the only email it sends is your daily summary, to yourself. By default Claude asks before sending any email; Step 6 shows how to let the daily summary go out on its own. ([Claude help: Google connectors](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors))

## Step 3: Connect your job sources

Claude needs at least one place to look for jobs. Connect as many as you can: more sources means more matches.

| Source | Best for | Cost | How to connect |
| --- | --- | --- | --- |
| Indeed | Canada, the US and many other countries | Free | **+** → **Connectors** → **Manage connectors** → **Browse connectors** → search "Indeed" → **Connect** → sign in |
| LinkedIn, through Apify | Anywhere LinkedIn is popular | $5 free credit a month, then a paid plan | Add Apify as a custom connector (steps below) |
| HiringCafe | Canada and the US; jobs straight from company career pages | Free | Optional. There's no public connector for it yet; if you have a HiringCafe connector address, add it as a custom connector named **HiringCafe Job Search**. Otherwise skip it. |

**Adding a custom connector** (for Apify):

1. Open **Settings**, then **Connectors**. In some accounts this is under **Customize → Connectors**.
2. Click **+ Add**, then **Add custom connector**.
3. Type the name **apify** and paste the address `https://mcp.apify.com`.
4. Click **Continue**, keep the settings Claude fills in, and click **Add**.
5. Sign in when the Apify page opens. If you don't have an account, create a free one there.

**Living outside Canada or the US?** Indeed and HiringCafe work best in North America. Other countries have their own popular job sites. Check the connector directory (**Browse connectors**) for the main job site in your country; if it's there, connect it and Claude will search it too. During setup, Claude will ask which site people in your country use.

**About Apify's free credit.** The free Apify plan gives $5 of credit each month. One daily LinkedIn search costs about $0.20 to $1.00, so the free credit usually lasts one to three weeks. When it runs out, Claude skips LinkedIn and keeps using your other sources until the credit renews. For LinkedIn every day, upgrade to a paid Apify plan ([check current prices](https://apify.com/pricing)). Don't open extra free accounts for more credit: [Apify's terms](https://docs.apify.com/legal/general-terms-and-conditions) allow one personal account per person.

([Claude help: connectors directory](https://support.claude.com/en/articles/11724452-use-the-connectors-directory-to-extend-claude-s-capabilities) · [custom connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) · [Apify: connect to Claude](https://docs.apify.com/platform/integrations/claude-desktop))

## Step 4: Install the skill (the .zip file)

The skill is the set of instructions that teaches Claude how to run your job hunt. It's the file **job-hunt-assistant.zip**. You install it once, by uploading it to your Claude account. That's all it needs: there is nothing else to connect for the skill itself.

1. **Download the skill.** On this project's [Releases page](../../releases/latest), click **job-hunt-assistant.zip**. (Or download **Job-Hunt-Assistant-Kit.zip**, which also has this guide as a PDF. Open the kit by double-clicking it on a Mac, or right-click → **Extract All** on Windows; **job-hunt-assistant.zip** is inside.)
2. **Leave job-hunt-assistant.zip as it is.** Don't open or unzip it. Claude needs the .zip file exactly as it is.
3. On your computer, go to **claude.ai** and open **Settings → Capabilities**.
4. Scroll down to **Skills** and click **Upload skill**.
5. In the window that opens, find **job-hunt-assistant.zip** (usually in Downloads) and choose it.
6. Wait a few seconds. **job-hunt-assistant** appears in your skills list. Make sure its switch is on.

**If the upload fails:** make sure you chose the file ending in **.zip**, not a folder. If you opened it by accident and it became a folder, download it again. Also check that Step 1 is done (**Code execution and file creation** must be on). The skill is private to your account; nobody else can see it.

## Step 5: The setup interview (about 10 minutes)

Start a new chat and type: **Use the job-hunt-assistant skill to set up my job hunt**. Naming the skill makes sure Claude uses it. Claude then asks about 8 short questions, one at a time. You can type "skip" for any of them and change your answer later.

| # | Claude asks about | Tip |
| --- | --- | --- |
| 1 | Your resume | Attach the PDF or Word file. Claude shows a summary, then asks you to fix anything wrong and add results with numbers (for example, "grew sales 20%"). |
| 2 | Contact details | Name, email, phone, LinkedIn, how you sign messages, and which email gets the daily summary. |
| 3 | Jobs you want | Claude suggests job titles from your resume. Keep, remove or add, and say what you don't want. |
| 4 | Location | Your city, how far you'll travel, and whether remote jobs count. |
| 5 | Pay | Your minimum yearly salary. Jobs that don't list pay still show up. |
| 6 | Employers | Industries you like, the smallest company size you'd join, and any to avoid. |
| 7 | Deal-breakers and strengths | Tools you've never used, languages you speak, and what you're great at. |
| 8 | Schedule | Which days and what time the search should run. |

When you're done, Claude:

1. Creates your **Job Application Tracker** page and saves your answers there. Only you can see it unless you share it.
2. Offers to look through Gmail for jobs you've already applied to. Say yes to see them in your tracker.
3. Offers to run the first search. Say yes; your first results arrive in a few minutes.

## Step 6: Turn on the daily run

At the end of setup, Claude offers to create two **scheduled tasks**: the daily job search and a short weekly review on Sundays. Say yes. They run in the cloud, so your computer can be off.

One setting matters. The daily run sends your summary email and saves files while nobody is watching, so it may wait for your approval. If the morning email doesn't arrive:

1. Click **Scheduled** in the left sidebar, or ask Claude: "Show my scheduled tasks."
2. Open the daily job hunt task.
3. Turn on **Automatically approve**.

To run the search any time by hand, type **Use the job-hunt-assistant skill to run my job hunt** in a new chat. ([Claude help: scheduled tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-cowork))

## Your daily routine (10 to 20 minutes)

1. Open the morning email and click **resumes and messages are here**.
2. Pick the jobs you like. On each, read **Lead with** and **What's thin**.
3. Download the resume: PDF to apply as is, Word if you want to edit it.
4. Apply on the company's website.
5. On LinkedIn, find the recruiter, the hiring manager and a team member (use **Find them on LinkedIn**). Send each their connection note with the **Copy** button, then the longer message once they accept.
6. In your tracker, open the job and click **I applied today**, and tick **Sent LinkedIn outreach**.

Claude watches Gmail for replies by itself. When a company invites you to an interview, interview prep notes appear in your tracker after the next run. You can also ask any time: "Make me an interview guide for the [company] role."

Found a job yourself? Paste the link into a chat, and Claude scores it and makes the resume and messages for it.

## What it costs

Only two things cost money: your Claude plan and, if you want LinkedIn every day, a paid Apify plan.

| Item | Cost |
| --- | --- |
| Claude | Your Claude plan (Pro or higher) |
| Indeed, Gmail (and HiringCafe, if you have it) | Free |
| LinkedIn through Apify | $5 free credit a month (about $0.20 to $1.00 per daily search), then a paid Apify plan |

Daily runs also count toward your Claude usage. If you hit your limits, set the search to weekdays only.

## If something goes wrong

| What you see | What to do |
| --- | --- |
| "Remaining usage isn't enough" from Apify, or LinkedIn skipped | Your free Apify credit is used up. Wait for it to renew next month, or upgrade your Apify plan. Your other sources keep working. |
| A job source "failed to connect" | Open **Settings → Connectors**, check that it's connected, reconnect it if needed, then try again. |
| No morning email | Turn on **Automatically approve** for the scheduled task (Step 6), and check that Gmail is connected (Step 2). |
| "No roles cleared 60%" | Normal on quiet days, especially weekends. If it happens all week, ask Claude to review your target job titles and filters. |
| Claude doesn't seem to use the skill | Check the skill's switch is on (**Settings → Capabilities → Skills**), then type "Use the job-hunt-assistant skill to run my job hunt" (or "…to set up my job hunt"). |
| A resume or message says something wrong | Tell Claude the correction (see the next section). |

## Make it yours: just ask Claude

If anything isn't working the way you like, tell Claude in plain words and it will change it. Nothing in this setup is fixed. For example:

- "Make the referral messages shorter and more casual."
- "The hiring manager messages sound too formal. Make them friendlier."
- "Don't mention my freelance work in resumes."
- "My team was 8 people, not 5."
- "Add product manager roles and stop showing sales roles."
- "Raise my minimum salary to 90,000."
- "Add a short cover letter for every job."

**Small changes about you** (your facts, your tone, the jobs you want) are saved in your profile and used from the next run.

**Bigger changes to how the skill works** (like adding cover letters, or changing how messages are built) are made in the skill itself. Claude shows you the updated skill, and you click to save it. If that option doesn't appear, Claude gives you a new skill file instead; upload it in **Settings → Capabilities → Skills** to replace the old one.

## Sources

- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [Use Google Workspace connectors](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors)
- [Use the connectors directory](https://support.claude.com/en/articles/11724452-use-the-connectors-directory-to-extend-claude-s-capabilities)
- [Get started with custom connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
- [Schedule recurring tasks](https://support.claude.com/en/articles/13854387-schedule-recurring-tasks-in-cowork)
- [Apify: connect to Claude](https://docs.apify.com/platform/integrations/claude-desktop)
- [Apify pricing](https://apify.com/pricing) · [Apify terms](https://docs.apify.com/legal/general-terms-and-conditions)
