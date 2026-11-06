Alannah Shinde
ICS 603 Fall 2026: Final Project Proposal
EventFlow: event intake assistant for ACM at UH Manoa
Project goal
A web app that helps ACM officers turn informal event announcements into reviewed event drafts,
filled in to match the ACM website's event form.
Intended user and problem
The user is an ACM officer who adds events to the ACM website through its admin form. The form
requires a title slug, image, description, event date and time, and kind, and also has optional location
and SIG fields. Announcements arrive as free text (a message, an email, a post), so the officer
re-types each detail by hand, picks the kind, the SIG, etc.
Some events could be missed, information on events could be wrong, and making a description for
the event can take a while. Only predetermined “kinds” of events can be selected and sometimes the
user is unsure what to classify them as (see the Kind list under Data source and access).
Although slug is a needed requirement, the ACM site generates it automatically, so EventFlow does
not have to draft it. The user will still need to upload an event image manually through the ACM
website.
Example input
Posted Oct 20, 2026 (Tuesday). “Resume Review Day! This Thursday 5-7pm in POST 318. Bring a
printed resume and ACM officers and industry volunteers will give you feedback. Pizza provided.”
Expected draft: Title “Resume Review Day”; Date 2026-10-22; Time 17:00; Location POST 318; SIG
blank (general ACM event); Kind Networking (the officer confirms); Description drawn only from the
text, including that it runs 5-7 PM, and worded in the style of past ACM event descriptions. “This
Thursday” is resolved using the posted date, and the officer confirms it.
Sample input set
Eight synthetic inputs with the result I expect. Real ACM announcements will replace or join them
where allowed (see Data source). Expected results assume the SIG list includes SWITCH, ICSpark,
8bit, Grey Hats, Ballroom Dance, PANDA and use the Kind list defined under Data source and access
(Workshop, Social, Talk, Hackathon, Networking, Competition, Meeting, Other). To test whether
EventFlow can detect potential scheduling conflicts, I may add a synthetic event to the database with
the same date, time, and location as one of the test inputs.
# Input (posted date) Expected result Type
1 Resume Review Day! This Thursday
5-7pm in POST 318. Bring a printed
resume... Pizza provided. (Oct 20)
All fields drafted as in the example above. date
2026-10-22, time 17:00, location POST 318, kind
Networking (confirmed by officer).
Synthetic
2 Intro to Git workshop, Nov 3, 6:00 PM,
Holmes Hall 244, hosted by the 8bit.
(Oct 20)
Title Intro to Git; date 2026-11-03; time 18:00;
location Holmes Hall 244; SIG 8bit; kind
Workshop.
Synthetic
# Input (posted date) Expected result Type
3 Come to our game night in the ACM
lounge, bring friends! (Oct 20)
Flag: date and time missing. Nothing saved. Synthetic
4 Career panel Nov 10 at 5pm with three
alumni. (Oct 20)
Date 2026-11-10; time 17:00; kind Talk (or
Networking, officer confirms). Location is optional,
so it is left blank with a notice, not an error or
inventing one.
Synthetic
5 Come hang out and build something
with us Friday at 6pm in POST 302.
(Oct 20)
Date 2026-10-23; time 18:00; location POST 302.
Kind is unclear, so it is flagged as uncertain
(Social or Other) and the officer picks.
Synthetic
6 Join us for the fall kickoff on Sept 15 at
6pm in POST 318. (Oct 20)
Flag: date is in the past. Synthetic
7 Study session Thursday Oct 22 at 6pm
in POST 318. (Oct 20)
Warning: same location on the same day as saved
Resume Review Day (shown with its 17:00 start
time). Needs confirmation before saving.
Synthetic
8 Thanks everyone who came to last
week's meeting! Great turnout. (Oct
20)
No event found. Message shown; nothing saved. Synthetic
All eight are synthetic and labeled that way. I will check that they resemble real ones by comparing
them against 5 or more of my own past ACM announcements (public posts, personal details
removed).
Expected result and value
After the officer approves, they see a structured draft of the text-based event fields in the same field
order as the ACM site's event form, with a copy button per field, and the event is saved with its
original announcement so they can find and reuse it later. To show it improves current work, I will time
5 announcements entered by hand versus with EventFlow, and count how many drafts with a missing
or wrong required field were caught before the officer entered them on the site.
Big-picture sketch
(1) box to put pasted announcement and posted date with TODAY button on side, (2) the drafted fields in
the ACM form's order, each with its source quote and a copy button (3) checks and flags, (4) similar past
events, (5) approve or reject (and edit) button, (6) saved events and search (says search: career events
[view original text])
Workflow or component sketch
? Later: flyer converts to webp? (needed to upload to site, but unnecessary to project right now)
? Semantic search?
? Do people want/can it be integrated with the site?
Update after instructor feedback (the sketch above is unchanged): in the “LLM extracts fields, chooses KIND”
step, the backend also loads up to two past saved descriptions of the same kind from the database and gives
them to the model as style examples only. Room names are normalized in code before the “same day?” rule
runs.
Data source and access
• Past ACM event announcements that were already posted publicly, plus synthetic announcements
I write myself. Personal details (phone numbers, personal emails, student names) will be removed
before use, however events do not typically have these. Past event descriptions already published
on the ACM site may also be used as style examples for the description (see LLM role).
• Kind list (single source of truth): Workshop, Social, Talk, Hackathon, Networking, Competition,
Meeting, Other. I will copy this list once, exactly, from the ACM site's event form, store it as the
Kinds reference table, and use that table everywhere (the model prompt, validation, sample
inputs). If the form differs from this list, the form wins and this proposal's examples are updated to
match.
• SIG list: copied by hand from the ACM site's event form (e.g. SWITCH, ICSpark, 8bit, Grey Hats,
Ballroom Dance, PANDA).
• Known rooms list: a short hand-made list of rooms ACM uses (e.g. POST 318, POST 302,
Holmes Hall 244), used to normalize locations (see Check and flag).
• These lists are reference data, not personal information.
• Permission: I will use only announcements I am allowed to share and ask the other officers before
using anything that was not public. No sensitive data and no PII. If any data might be sensitive I
will contact the instructors before collecting it.
Up to three core features
1 Extract and classify: from pasted text, draft title, date, time, location, SIG, description, and a kind
from the Kind list, each with the quote it came from. The description is worded in the style of past
ACM descriptions, but every fact in it comes only from the announcement.
2 Check and flag with exact rules: missing required field (title, date, time, description), date in the
past, kind not in the list, and a warning when a saved event has the same location on the same
day. Locations are normalized in code first (uppercase, spaces and punctuation removed,
matched against the known rooms list), so “POST318” and “POST 318” count as the same room.
3 Review, save, and search: the officer approves, edits, or rejects; approved drafts are saved with
their announcement and shown in the ACM form's field order with copy buttons; past events can
be searched by meaning.
LLM role
The model reads the announcement text, the posted date, the SIG list, the Kind list, and up to two
past event descriptions as style examples. It returns title, date (ISO, YYYY-MM-DD), time (24-hour,
HH:MM), location, description (1 to 3 sentences, including the end time if one is mentioned), sig (a
name from the list, or empty), kind (one value from the list), a list of missing fields, a list of uncertain
fields, and a source quote for each field. It must not invent values: anything absent from the text is left
empty and flagged. The slug is not written by the model since it already is written by the ACM
website.
Style examples for the description. Limiting the description to facts in the text can make it flat, so
the prompt includes one or two past saved descriptions as examples of ACM's tone, length, and
phrasing. In version one these are the most recent saved events of the same kind (or the most recent
events overall if none exist yet). The prompt tells the model that the examples are for style only: facts
(names, dates, times, rooms, food, speakers) must come from the new announcement, and nothing
from an example may be copied in as a fact. The description's source quote must still come from the
announcement, and the officer reviews it before saving. Later, once semantic search exists
(Embeddings and RAG lessons), the examples can be the most similar past events instead of the
most recent.
Data use
The app looks up the Kind, SIG, and known rooms lists to validate the model's choices; the saved
events to detect same-location, same-day events and to find similar events; and the saved
descriptions to pick style examples for the prompt. It never reads member accounts or personal
information.
Saved records
Linked record types, all kept after a restart:
• Announcements: original text, posted date, when it was entered.
• Events: title, description, event date and time, location (as the officer approved it, plus a
normalized location key used for the same-day check), optional SIG, and kind, linked to one
announcement.
• SIGs and Kinds: reference lists that events point to.
• Review decisions: what the officer approved, edited, or rejected for each field.
An announcement produces zero or one event; an event has one kind and at most one SIG; a SIG or
kind can have many events.
In the first version, extracted drafts will remain unsaved until the officer approves them. Once
approved, the application will save the original announcement, reviewed event fields, and review
decisions in a persistent SQLite database. Rejected or incomplete drafts will not be saved, and
existing records will be unchanged.
Searchable text
Event descriptions and original announcements. An officer might search “career events for new
students” to find similar past events and reuse their wording. Later I will test whether semantic search
beats keyword search, and whether it picks better style examples for new descriptions than “most
recent of the same kind.”
Human review
Every drafted field is shown with its source quote. The officer approves, edits, or rejects before
anything is saved. Relative dates (“this Thursday”), uncertain kinds, and same-day location warnings
always need confirmation. The original text stays visible. In version one the officer copies the
approved fields into the ACM site's form themselves.
Same-day location warning. The warning compares normalized location and date, and shows the
existing event's title and start time so the officer can see at a glance whether it is a real overlap or just
two events in the same room at different times. It is a warning, not a block, so a false alarm costs one
click. I am keeping the check day-level for version one because end times are outside version one
(sample input 7 starts at 18:00 inside a 17:00-19:00 event, which a start-time-only comparison would
miss). Comparing start times, and later end times, is a possible refinement.
One failure case
Input: “Come to our game night in the ACM lounge, bring friends!” (no date or time). What fails: the
date and time cannot be determined. What the user sees: “Date missing” and “Time missing”
highlighted, and the save button disabled until they provide them. What must remain unchanged: no
event is created, existing events are untouched, and the pasted text stays in the box so they can add
the details and run it again.
Three acceptance criteria
1 Given the Kind and SIG lists are loaded and no saved event is at POST 318 on 2026-10-22, when
the officer pastes sample input 1 and approves the draft, then an event is saved (title Resume
Review Day, 2026-10-22 17:00, POST 318, kind Networking as confirmed), linked to its
announcement, and still listed after a restart.
2 Given an announcement with no date or time (sample input 3), when extraction runs, then the app
flags the date and time as missing, does not guess them, and creates no event.
3 Given a saved event at POST 318 on 2026-10-22, when the officer tries to save sample input 7
(same location, same day, even if typed as “POST318”), then the app shows a warning that
includes the existing event's start time, requires explicit confirmation before saving, and leaves the
existing event unchanged.
Outside version one
• Submitting events into the ACM site automatically (needs API or database access I do not have
yet).
• Flyer image upload, OCR or vision reading, and image compression and WebP conversion.
• Multiple events in one announcement or a batch of announcements, recurring events, end-time
checks.
• Choosing style examples by semantic similarity (version one uses the most recent same-kind
events).
Open questions
Decisions to make
• Resolved: location matching will be done in code for version one: uppercase, remove spaces and
punctuation (“POST318” becomes “POST 318”), then match against the known rooms list. A
location not on the list is kept as written, compared by its normalized text, and shown with a notice.
• How many style examples help without hurting accuracy (one or two), and whether to take them
from the same kind or from the same SIG.
Technical details I will learn later
• Which model and structured-output method to use through the course gateway.
• How semantic search will work (including for choosing style examples) and how to deploy the app.
• Whether the ACM site has an API (ask whoever maintains it), and whether the gateway model
accepts images for a later flyer feature.
Next investigation
Biggest uncertainty: how reliably the model extracts correct fields, especially dates, times, and kind,
without inventing values. I will run the 8 sample inputs, plus 5 or more real public ACM
announcements with personal details removed, through the course model and record each field as
correct, missing, or wrong. If dates or kinds are unreliable, I will narrow version one to explicit dates
and require the officer to confirm every date and kind.
A second check, on the new style examples: for 5 of the announcements, generate the description
with and without past descriptions in the prompt, and compare them for sound and ACM wording, and
check that no fact from an example leaked into the new description. If leaks show up, I will drop the
examples or tighten the prompt.
A third small check: ask whoever maintains the ACM site whether an API exists, which decides
whether pushing events into the site is a realistic later step.