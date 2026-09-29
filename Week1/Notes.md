# Week 1 Notes

## Reproduceable environments

- Ensure code is correct, unit tests, integration tests, end to end tests
- Machine - Can't check unreproducable machine. Pin, Check and Prove. Same behaviour, not similar. Works when given a repo or another machine.
- Isolate - Create boundary
- Pin - Direct requirements with double equals, specifying exactly one file
- Lock - The fully resolved tree, transitive dependencies included, commited.
- Proof of steps - Delete environment and rebuild it from the repo alone.

## Code

### 3 Gates, 3 Questions

1. Ruff - static testing (Is code shaped like working code)
2. MyPy - Do type claims actually hold
3. Pytest - Does the code does what it says it does. Can't test on what it is not told to test on.

- Types before tests
- Each dependent on the step before
- Ruff and Mypy does not run the code
- Pytest checks code is sufficient, but blind to what was not tested using it. Only checks behaviour it was specified.
- Unannotated functions are invisible to type checkers.
- Construct decimal from a string.

<u>Day 2</u>

* Commit, Branch, Merge, Review
  * Review - Deciding whether the change is right. Asks for correctness
  * Merge - Ensure to changes can coexist
  * Branch - Claim about a change. A pointer
  * Commit- Claim about a change
* Commit
  * Snapshot of a tree
  * A commit is not a diff, it is a snapshot
  * A pointer to its parent
  * A message
  * Git computes diffs on demand, by comparing snapshots
  * Subject of commit says what, Body of a commit says why
  * If you can't say why, you maybe commiting something you do not need to.
* Branch
  * Deleting a branch, does not delete commits, only the pointer
  * A file containiing a commit hash
* Merge
  * Finds common ancestor, compares changes since then, decides if they can be combined
  * Almost nothing destroys pointers
  * git reflog = shows all positions HEAD held
  * git rest --hard = Moves pointer
  * If there is a merge conflict, git asks the user what to include
  * git diff --stat file1 file2 = shows file names changes
  * ORT merge strategy
  * 
* Code Reviews
  * * Say what should change and why
    * File list shows us the shape and scope of the change
    * WHERE - File and line
    * WHAT - Once sentence
    * CLASS - Machine if a gate should have caught it, or human if only a person could
    * ASK - What you want the author to do
* Pass Bar
  * At least one machine finding, with the gate output referenced
  * The boundary bug found, and classified HUMAN
  * At least one of
    * a tautological test
    * Missing boundary test
    * Swept in change
  * Every finding carries a class
  * Verdict of request changes, with a reason naming a HUMAN finding
