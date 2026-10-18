Why did you set your relevance floor where you did, and what happened when you tried other values?

- Different floor values were evaluated and it was decided to go with a floor value of 0.3.
- This was due to it providing a good balance between being able to answer all unanswerable questions and refusing all unaswerable questions. It was able to achieve this with 777 average input tokens. Lower relevance floors led to results that used more average input tokens such as with 0.2 using 895 average input tokens. Higher relevance floors led to some questions to be missed such as at 0.4 where q28,q54 were incorrectly refused and q62 was answered incorrectly. Relevance floors above this led to exponentially more questions to be refused.

---

Would you chunk your documents? Why or why not, given their length and shape?

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

  - Embedded 71 questions once (929 tokens), reused for every strategy.
  - Retrieval Evaluation
```
strategy                 R@1   R@3   R@5    MRR  ctx words  top ans  top unans
------------------------------------------------------------------------------
whole_document          0.89  1.00  1.00   0.94        491     0.56       0.51
fixed_100               0.75  0.94  0.97   0.84        266     0.60       0.52
fixed_overlap_25        0.73  0.94  0.98   0.84        272     0.59       0.53
sentenced_100           0.83  0.94  0.97   0.88        249     0.59       0.53
sections_plain          0.89  0.98  1.00   0.94        344     0.58       0.52
sections_contextual     0.86  1.00  1.00   0.92        356     0.57       0.52

Missed at k=3:
  whole_document         none
  fixed_100              q15, q49, q58, q60
  fixed_overlap_25       q21, q35, q49, q62
  sentenced_100          q49, q53, q54, q58
  sections_plain         q62
  sections_contextual    none

Saved eval_results/retrieval.json
```
  - From the retrieval results we found that the 2 best performing strategies involved the whole document and sections_plain with an MRR score of 0.94 and 0.92 respectively as well as an R@1 score of 0.89 and 0.86. 
  - In terms of question responses that missed context, sections_plain missed q62 which was a kind that involved a rare term while whole_document did not miss terms. 
  - Whole document uses the most context words at 491 compared to sections_plain 344 but gives the most accurate results. There is also a clear seperations between the unanserable and unanswerable questions.
  - As a result it was decided to keep using whole documents rather than chunking them. The contents of the documents involved statistics at the start and a block of text with backround information around the statistics. As a result it made sense to search with whole documents given their low word count leading it to be less likely relevant context would be missed.
  - For the max iteration limit for when tools are used to answer questions, I gave a limit of 15. This was due to questions that involved analysing all borrowers potentially requiring multiple calls to calculations as well as record searches. 

---

What is the worst wrong answer your system could give, and what stops it?

- The worst wrong answer the system could give, could be based on unfounded claims (hallucinations) and using context that is irrelevant to the prompt that was used. In order to prevent this, I stated in the prompt to cite source documents from which claims are based off.
- To prevent irrelevant sources being used as context, a relevance floor was used to ensure only retrieved context that was scored above the relevance floor could be used as context. If no sources above the relevance floor could be retrieved, the query is rejected. This allowed for the model to ensure that the model could only answer questions that it had enough relevant context on.
