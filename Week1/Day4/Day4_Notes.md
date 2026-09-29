# Spec Driven AI Delivery

* Dont want to introduce security vulnerabilities.
* Only run calude in directory you are working on
* Check your own build against each one. Do not guess requirements.
  * Specify a boundary test
  * A ticket already closed is skipped, not treated as an error. Do not try to close closed tickets
  * Closing records  => who closed it as "system", not a person
  * Do not email a customer automatically incase the reply is incorrect or there are other issues.
  * Do not change the reply deadline
* Do not leave business requirements up to Claude.
* Process
  * FRAME
    * Write the spec. Correct the one Claude drafts
  * DIRECT
    * One task at a time
  * VERIFY
    * Check the task against what the spec said.
  * OWN
    * Be able to explain every line you keep
* Spec - About a page including all sections. A file in a project. **Commited before the code**
  1. **Why** - The problem in two lines.
  2. **What** - The behaviour, with real numbers and the edge cases.
  3. **Context** - What already exists that this has to fit into. What Claude needs that it does not already have
  4. **Constraints** - What it must not do, and what is out of scope.
     1. constraints - What not to mess with e.g. no new dependencies, no ui elements, no emails to customers
     2. out of scope - May want to do, but not part of main task e.g. generating report on all tickets in last week.
  5. **Tasks** - Small, numbered, each with a vercify line. Small enough to review in one sitting. Enough to commit on its own.
  6. **Done** - One check for the whole feature.
     1. Check what we built actually works.
     2. Each task can have its own check
* Make prompts specific and precise. Leave as little as possible up to interpretation
* Avoid words open to interpetation. e.g. old, recent, large, sensibly, properly.
* Agents are eager. It can add a bunch of features that were never asked of it or needed. Specify what is out of scope
* Context
  * All the things the agent cannot see. e.g. files, code, patterns
* How big should a spec be?
  * Bug fix - Why, what, one task, skip rest
  * Small feature a few tasks - All six parts, one page, two or three tasks
  * Ten files or more - Two specs. It is more than one piece of work
* Can ask AI to make a spec, going back and forth asking questions. Attach spec as context on future work
* Write a short spec, to give the AI, commit it alongside the code. Give it one task at a time. Check each change before taking the next step. You should be able to explain all the code.
