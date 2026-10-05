Robust Services

* Idempotency and timeouts. Make contract survive retries and survive its own blocking code
* Account for what happens when services fail
* Idempotency (Call it once or 100 times, the state stays the same):
  * 2 same exact post requests create two different objects. End up with duplicate records after a retry. Want to avoid this.
  * Use an idempotency key
  * Does not mean gives the same response
  * What happens if we make the same call multiple times?
  * PUT is idempotent as the same update ends up with the same state
  * POST is not idempotent. We will create a new state in our app, with an extra record.
  * Idempotency key:
    * Client attaches key: A header it generated itself, before the first attempt
    * Server remembers it: First time it sees a key, do the work and stores the result against it.
    * Repeat returns the original: Same key again, hand back the firm already created.
    * CLIENT GENERATES THE KEY, NOT THE SERVER
  * Timeouts:
    * Calling a slow endpoint, you choose the timeout. How long are you going to wait for a response?
    * Each service is a dependency in a chain. Including yours.
    * FastAPI runs all async functions in one event loop in one thread.
    * How to resolve blocking method:
      * Don't use async - Runs synchronous methods in its own thread
      * Need async, but the work blocks - Hand it to a thread explicitly, rather than running it on the event loop. await run_in_threadpool(...)
      * If a route does not await anything, it should not be async def
  * Prioritise issues to be fixed - justify prioritisation
  *
