Objectives of the firm intelligence API:

* ability to generate an index for firm documents
* ability ro query a db of documents
* ability to trace documents that weere used to generate an answer
* ability to see the cost of any given call to the model
* ability to refuse an aswer if nothing relevant exists ()relevance score is too low) rather than guess
* ability to retry a request safely (without creating duplicate records). **Idempotency**
* **NEXT** - ability to let the model decide for itself whether it needs to search rather than always search
* ability to generate a validated, structured analysis of a firm
* ability to stream a response as it is being generated, rather than waiting for the whole thing to finish.
* Ability to prove the service still runs/behaves correctly after a change... automatically

## Part 0

* Setup venv with appropriate dependencies (pydantic, pytest, chroma etc)
* 

## Part 1 - Getting the Documents Ready

* 8 documents sitting in a file each has an id,title plus a block of text.
* Someone triggers indexing... one of request that tells the service to index the documents (convert documents into embeddings). Tells service to read all of this now.
* We start by reading just the text of each document, ready to send off.

## Part 2 - Turning the documents into numbers

* All texts are sent together, single request to Voyage
* Voyage reads each one and turns it into a list of numbers representing what it means.
* Eight list of numbers (one per doc), how many tokens that cost.

## Part 3 - Storing them

* Each docs numbers get handed to Chroma (plus id, title and original text)
* Chroma saves all of this to disk (our data persistence)
* NOTE: nothing can be searched until this step has actually happened once.

## [*] Part 4 - A question comes in

* User sends a question to the service
* We trigger relevant functions at that endpoint -
  * checks its long enough + the extra settings are valid
* An invalid question gets rejected straight away - nothing else would run

## Part 5 - The question becomes a vector

* The questions text gets sent to Voyage (same as the docs)
* It comes back as a list of numbers (the same shape as the docs)

## Part 6 - Find the closest documents

* The question's numbrs get compared against every docs numbers that are already in Chroma.
* NOTE - This comparison measures how close each doc is to the question (it does this in meaning, not wording).
* The closest few come back (ranked and carrying a score).

## Part 7 - Decide whether its worth answering

* Each returned docs score gets checked against our RELEVANCE_FLOOR.
* Anything that doesn't clear the bar gets thrown away
* If nothing clears the bar our service stops here.
  * Says it can't answer  No further action

## Part 8 - Preparing what the model will see

* The docs that did clear the bar get combined into one block of text.
  * Each one keeps its id and title attached (So it can be referenced/pointed back to later)
* That block, plus the orignal question is ALL the model knows. (GROUNDED)

## Part 9 - Get an answer

* That block and the question get sent to Anthropic
* The SYSTEM_PROMPT tells the model ahead of time that it can only use what is given
* It reads everything it was given and write a response
  * in the response it marks which document each part of the answer came from

## Part 10 - Sending the answer back

* Answer comes back, alond with how much was spent

  * Input output tokens and stop reason
* The service assembles the final response (answer, which docs were used, how relevant each one was, and what it cost)
* Response goes back to whoever asked the original question.
* 

# Tools and Interfaces

* Tool use and the context engineering that quietly runs underneah it
* Describe - Name, description, JSON schema for its input. Nothing runs yet
* Model asks to use it - **stop_reason comes back as tool_use, with arguments it wantes to call it with**
* Code runs it - **Model never executes anything. It asks, You decide whether to comply**
* Hand back the result, loop - Same conversation continue until
* At each round the **context grows**. Tool use request gets appended too. **Tool result gets appended as well under role : user not a special role.**
* User, Assistant and System
* Tool result is the next user turn.
* This is context engineering
* **There is a limit to the context window size**
* Repair and Retry loop:
  * If an error occurs in using a tool, the model is told it is an error and a reason. The agent then recalls again with adjusted paramemters. This can loop multiple times.
  * The field that does the work: is_error = True
  * tool_calls_made only increment on success.


We cap tool use loop as each call to a tool, has a cost associated with it.
