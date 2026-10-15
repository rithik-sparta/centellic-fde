- Why did you set your relevance floor where you did, and what happened when you tried other values?
- I have set the relevance floor to be at 0.4. This value was chosen as relevance floors of 0.3 and below included less relevant sources such as Q1, relevance_floor 0.3 with doc-09, which is an internal rating review for Aldergate Business Solutions initial internal rating review and not related to Northbridge Components. Relevance floor values of 0.4 and above would start removing relevant documents such as doc-11 from context as their score does not pass the relevance floor.
- Would you chunk your documents? Why or why not, given their length and shape?

  - Here are the word counts for each of the documents:

    - | Document Id | Word Count |
      | ----------- | ---------- |
      | doc-01      | 79         |
      | doc-02      | 74         |
      | doc-03      | 78         |
      | doc-04      | 138        |
      | doc-05      | 145        |
      | doc-06      | 81         |
      | doc-07      | 121        |
      | doc-08      | 77         |
      | doc-09      | 99         |
      | doc-10      | 114        |
      | doc-11      | 388        |
      | doc-12      | 226        |
    - As the word count of each document is relatively short, chunking would not deliver much of an impact on the retrieval performance.
- What is the worst wrong answer your system could give, and what stops it?

  - The worst wrong answer the system could give, could be based on unfounded claims (hallucinations) and using context that is irrelevant to the prompt that was used. In order to prevent this, I stated in the prompt to cite source documents from which claims are based off.
  - To prevent irrelevant sources being used as context, a relevance floor was used to ensure only retrieved context that was scored above the relevance floor could be used as context. If no sources above the relevance floor could be retrieved, the query is rejected. This allowed for the model to ensure that the model could only answer questions that it had enough relevant context on.
