* Weekly Assessment
* Input Schema - Shape arguments we send
  * If we have multiple arguments it would be a list of dictionaries,otherwise just a dictionary
* Model turns need to be represented exactly as it was sent
* Models can only request to use the tool, not use it directly
* Why not call build index if it does not exist
  * Once we switched to the vector db, this is stored on disk, so we no longer have to do this as the embeddings are persisted.

## Key Takeaways
