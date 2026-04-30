You are helping me migrate from TickTick to Apple Reminders + Apple Calendar using TickTick MCP and Apple Reminders/Calendar MCP.

Objective:
Move my active, important TickTick system into Apple Reminders and Apple Calendar safely, without creating duplicates, losing context, or over-migrating stale tasks.

New system design:
- Apple Reminders = source of truth for actionable tasks
- Apple Calendar = source of truth for recurring routines, time blocks, appointments, protected focus sessions, and scheduled rhythms
- Outlook = main email/calendar aggregation and offline client
- Endel = focus sound / Pomodoro replacement
- Bee / Gemini / Claude / MCP = automation and organization layer
- Obsidian or plain text = durable migration log, project notes, and reference archive
- TickTick = read-only fallback after migration, then retired if no longer needed

Primary principles:
1. Do not create duplicate sources of truth.
2. Do not migrate everything blindly.
3. Do not delete, complete, or archive TickTick tasks during migration.
4. Prefer Apple Calendar for routines and protected time.
5. Prefer Apple Reminders for concrete actions.
6. Skip Pomodoro history, habit streak history, and stale low-value tasks.
7. Every migrated Apple item must include a rollback marker.
8. Migration is not successful until verified.

Available tools:
- TickTick MCP:
  Read TickTick tasks, projects/lists, priorities, pins, due dates, recurrence, notes, subtasks, tags, completed state, and metadata if available.

- Apple Reminders MCP:
  Create, update, search, and verify reminders, lists, tags, due dates, notes, priorities, and subtasks if supported.

- Apple Calendar MCP:
  Create, update, search, and verify calendar events, recurring events, time blocks, and busy/free status if supported.

Migration batch marker:
Use this marker on every created Apple item:

MIGRATION_BATCH: ticktick-to-apple-YYYY-MM-DD

Replace YYYY-MM-DD with today’s actual date.

Every migrated reminder should include:
- Tag: #migrated-ticktick, if tags are supported
- Notes marker: MIGRATION_BATCH: ticktick-to-apple-YYYY-MM-DD

Every migrated calendar event should include:
- Description marker: MIGRATION_BATCH: ticktick-to-apple-YYYY-MM-DD

Migration scope:
Migrate only:
1. Pinned TickTick tasks
2. High-priority TickTick tasks
3. Tasks due today
4. Overdue tasks
5. Active recurring tasks that represent real obligations
6. Active project tasks that clearly need to remain actionable
7. Tasks with explicit start/end times or calendar-like meaning

Do not migrate:
1. Completed tasks
2. Old stale tasks with no due date and no clear current relevance
3. Low-priority someday/maybe tasks unless pinned
4. Pomodoro history
5. Habit streak history
6. Focus-session history
7. Duplicate tasks
8. Pure notes, references, or ideas
9. Tasks whose meaning is too unclear to classify safely

Classification rules:
Classify each TickTick item as exactly one of:

1. Apple Reminder
2. Apple Calendar event
3. Both Reminder + Calendar event
4. Reference / Obsidian candidate
5. Skip stale
6. Needs review

Use Apple Reminders when the item is:
- a concrete action
- an errand
- a call
- an email
- a purchase
- a form/submission
- a follow-up
- a checklist
- a deadline reminder
- a small task that does not require a protected time block

Use Apple Calendar when the item is:
- a recurring routine
- a time block
- a meeting
- an appointment
- a study session
- a focus session
- a weekly review
- a cleaning/admin block
- exercise or running
- prayer/reading/study rhythm
- sleep/wind-down routine
- anything with start and end time
- anything that consumes protected time

Use Both when:
- the item needs protected time and also has a concrete deliverable
- example:
  Calendar event: “Sermon prep — Saturday 9:00–11:00”
  Reminder: “Draft Sunday sermon outline”

Use Reference / Obsidian candidate when:
- the item is mostly background
- the item is a note, idea, quote, project context, or reading reference
- the item should be preserved but not treated as a task

Use Skip stale when:
- the item is old, inactive, low-priority, not pinned, not due, and not clearly relevant

Use Needs review when:
- destination is ambiguous
- recurrence is unclear
- duplicate risk is high
- task seems psychologically aspirational rather than actionable
- task may require manual rewriting
- task depends on old context that is not obvious

Priority mapping:
- TickTick high priority → Apple Reminders High priority
- TickTick medium priority → Apple Reminders Medium priority
- TickTick low/no priority → Apple Reminders No priority, unless pinned
- Pinned TickTick task → add #pinned tag if supported and place in Important list if appropriate

Suggested Apple Reminders lists:
- Inbox
- Important
- Admin
- School
- Church
- Home
- Errands
- Waiting
- Someday
- Projects

Suggested tags:
- #migrated-ticktick
- #pinned
- #deep
- #quick
- #errand
- #waiting
- #school
- #church
- #home
- #admin
- #clarify

Reminder creation rules:
When creating an Apple Reminder:
1. Preserve the task title unless it is vague.
2. If vague, prefix with “Clarify: ”.
3. Preserve due date and due time when available.
4. Preserve priority according to the mapping above.
5. Preserve notes in the reminder notes/body.
6. Preserve subtasks as subtasks/checklist items if supported.
7. Add #migrated-ticktick.
8. Add #pinned if the original TickTick task was pinned.
9. Add source metadata in the notes:

Migrated from TickTick
MIGRATION_BATCH: ticktick-to-apple-YYYY-MM-DD
Original TickTick title:
Original list/project:
Original priority:
Original due date:
Original recurrence:
Original tags:
Original URL or ID, if available:
Original notes:

Calendar creation rules:
When creating an Apple Calendar event:
1. Use a concise, action-oriented title.
2. Preserve recurrence when clear.
3. Preserve start/end time when available.
4. If no end time exists, infer a conservative duration:
   - quick admin: 15–30 minutes
   - normal task block: 45–60 minutes
   - deep work/study: 90 minutes
   - weekly review: 45–60 minutes
   If uncertain, classify as Needs review instead of guessing.
5. Mark real commitments and focus blocks as Busy.
6. Mark flexible routines as Free or Tentative if supported.
7. Add source metadata to the event description:

Migrated from TickTick
MIGRATION_BATCH: ticktick-to-apple-YYYY-MM-DD
Original TickTick title:
Original list/project:
Original priority:
Original due date:
Original recurrence:
Original tags:
Original URL or ID, if available:
Original notes:

Recurring item rules:
1. If recurrence means “do this action by a certain date/time,” use Apple Reminders.
   Example: “Pay rent monthly.”

2. If recurrence means “occupy this block of time,” use Apple Calendar.
   Example: “Run every morning 7:30–8:00.”

3. If recurrence is a routine, rhythm, study block, exercise block, weekly review, reading/prayer rhythm, or Endel focus block, use Apple Calendar.

4. If recurrence is vague, aspirational, or likely to create noise, mark Needs review.

5. Be careful with recurring reminders that contain subtasks. Flag them for review if behavior may not preserve the intended workflow.

6. Do not migrate Pomodoro sessions, focus-session history, habit streaks, or productivity statistics.

Duplicate prevention:
Before creating any Apple Reminder or Calendar event:
1. Search existing Apple Reminders and Apple Calendar for similar title, due date, recurrence, and notes.
2. If a likely duplicate exists, do not create a duplicate.
3. If a matching item exists but lacks migration metadata, classify as Needs review before modifying.
4. If uncertain, add to Needs review.
5. Never create both a Reminder and Calendar event unless the item clearly requires both a task and protected time.

Pre-migration dry run:
Before writing anything:
1. Inventory TickTick items in scope:
   - pinned tasks
   - high-priority tasks
   - due today tasks
   - overdue tasks
   - active recurring tasks
   - tasks with start/end times or calendar-like meaning
   - active project tasks with clear current relevance

2. Classify each item as:
   - Apple Reminder
   - Apple Calendar event
   - Both
   - Reference / Obsidian candidate
   - Skip stale
   - Needs review

3. Produce a migration table with these columns:
   - TickTick task
   - Source list/project
   - Classification
   - Destination
   - Due date/time
   - Recurrence
   - Priority
   - Proposed action
   - Notes / risk

4. Do not create, edit, delete, complete, or archive anything during dry run.

5. Wait for explicit approval before performing write actions.

Migration execution:
After explicit approval:
1. Process only high-confidence items.
2. Process in small batches of 25–50 items.
3. After each batch, verify that created Apple items exist.
4. Validate title, date, recurrence, priority, notes, tags, and migration marker.
5. If more than 5% of a batch fails validation, stop immediately and report errors.
6. Do not continue if authentication, permissions, calendar access, reminder access, or recurrence creation fails.
7. Do not retry failed write operations more than once automatically.
8. Preserve failed items in the migration report.

Migration log:
Create and maintain a migration log in plain text or Markdown.

For every created Apple item, record:
- migration batch marker
- timestamp
- original TickTick task ID or URL if available
- original TickTick title
- original TickTick list/project
- original due date/time
- original recurrence
- destination app
- destination list/calendar
- destination reminder/event ID if available
- created Apple title
- validation status
- notes/errors

The migration log should have these sections:
1. Migrated to Apple Reminders
2. Migrated to Apple Calendar
3. Created as both Reminder + Calendar event
4. Skipped as stale/completed/low-value
5. Needs manual review
6. Possible duplicates detected
7. Reference / Obsidian candidates
8. Failed items / errors
9. TickTick features not migrated

Verification:
Do not treat migration as successful until a verification pass confirms:
1. Every created Apple Reminder exists.
2. Every created Apple Calendar event exists.
3. Every migrated item has the correct title.
4. Every migrated item has the expected date/time.
5. Every migrated recurring item has the correct recurrence.
6. Every migrated reminder has the correct priority.
7. Every migrated item has the migration marker.
8. No obvious duplicates were created.
9. Pinned TickTick tasks were migrated or explicitly marked Needs review.
10. High-priority TickTick tasks were migrated or explicitly marked Needs review.
11. Calendar routines appear in the expected calendar.
12. Relevant calendar events appear in Outlook if expected.

Post-migration audit:
Run these checks:
1. Compare count of TickTick pinned tasks vs migrated pinned Apple items.
2. Compare count of TickTick high-priority tasks vs migrated high-priority Apple reminders.
3. Compare recurring TickTick routines vs Apple Calendar recurring events.
4. Check for duplicate reminders/events with similar titles and dates.
5. Check for orphaned calendar blocks that should also have reminders.
6. Check for reminders with no due date that should be scheduled.
7. Check for vague tasks beginning with “Clarify:”.
8. Check for tasks that should have been moved to Obsidian instead of Reminders.
9. Check for recurring items accidentally duplicated as both recurring Reminder and recurring Calendar event.
10. Check whether Apple Calendar events appear correctly in Outlook where expected.

Rollback plan:
If the migration is wrong, use the migration log and migration markers to identify all Apple Reminders and Calendar events created during the migration.

Rollback search criteria:
- Reminders tagged #migrated-ticktick
- Reminders with notes containing MIGRATION_BATCH: ticktick-to-apple-YYYY-MM-DD
- Calendar events with description containing MIGRATION_BATCH: ticktick-to-apple-YYYY-MM-DD

Rollback process:
1. Do not delete anything immediately.
2. Produce a rollback preview table with:
   - destination app
   - title
   - due date/time
   - recurrence
   - original TickTick task/list if available
   - proposed rollback action
3. Wait for explicit approval before deleting or modifying anything.
4. Never delete TickTick originals during rollback.
5. If deletion is unavailable through MCP, move incorrect Reminders to a list called “Migration Cleanup.”
6. If calendar deletion is unavailable, rename incorrect Calendar events with prefix “[REVIEW DELETE]”.
7. Preserve the migration log permanently.

Fallback plan:
1. Keep TickTick read-only for 30–60 days after migration.
2. Do not renew, cancel, delete, or clean up TickTick until the Apple Reminders/Calendar workflow is proven stable.
3. During fallback period, do not add new tasks to TickTick unless Apple Reminders/Calendar automation fails.
4. If Apple workflow fails, continue using TickTick as the fallback source of truth.
5. If Apple workflow succeeds, export or archive TickTick before canceling or deleting anything.

Cleanup plan:
After 30–60 days, perform final cleanup only if:
1. Pinned tasks migrated correctly.
2. High-priority tasks migrated correctly.
3. Recurring routines are correctly represented in Calendar.
4. Active reminders appear correctly in Apple Reminders Today/Scheduled views.
5. Outlook shows relevant calendar events if expected.
6. Bee/Gemini/Claude/MCP can read and manipulate the new Apple Reminders/Calendar setup reliably.
7. No major duplicate or recurrence problems remain.
8. The migration log has been saved permanently.

Only after final review:
- optionally archive TickTick
- optionally export TickTick
- optionally cancel TickTick renewal
- optionally delete old TickTick tasks, but only after explicit approval

Error handling:
If permissions, sync, or MCP errors occur:
1. Stop the current batch.
2. Report the failed item and exact error.
3. Do not retry more than once automatically.
4. Do not continue if the error affects authentication, permissions, calendar access, reminder access, recurrence, or write operations.
5. Preserve the migration log even for failed items.
6. Add failed items to the migration report.
7. Do not make compensating edits unless explicitly approved.

Final output after migration:
Provide a concise report with:
- number of TickTick items inspected
- number of Apple Reminders created
- number of Apple Calendar events created
- number of items created as both Reminder + Calendar event
- number of skipped items
- number of duplicate candidates
- number of items needing review
- number of failed items
- path or location of migration log
- summary of any risks or unresolved issues

Operating rule:
When uncertain, do not migrate automatically. Mark Needs review instead.
