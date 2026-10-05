Problems found

1. GET reports/{report_id} - Modifies the view count. If the same user runs this method twice, the view count will go up by 2, eventhough only one user viewed it.
2. POST reports/ - Not idempotent, user can send same request twice unintentionally, creating duplicate entries with different ids.
3. PUT reports/{report_id} - Not idempotent eventhough PUT is designed to be. We will end up appending to revisions. So multiple same calls will result in the revisions array containing duplicate entries.
4. GET reports/{report_id}/export - Can block other async processes running on the same event loop. If we have thousands of requests to this endpoint, it can take a while for new requests to get a response. Caller would have to wait for the response, if the server is under load.
5. DELETE reports/{report_id} - Does not delete the _view_counts key associated with the report being deleted. Not a problem currently, unless we create an object with the same id. If we delete reports can be a problem. e.g.
   1. beginning of state| report ids in REPORTS: {1 2} | view count of 2 is 5 for example
   2. delete id 2 | report ids in REPORTS : {1}  view count record still exists
   3. create a report | report ids in REPORTS: {1 2} view count record is 2: 5, eventhough it is a new report that no one has seen.

- Is it actually a problem, or just unfamiliar?
- What would a caller *see* when it goes wrong?
- Is it a problem today, or only under load / on a flaky network?

Priority

5 -  View counts will not be deleted when the report is deleted. If a new report with the same id is generated in the future, there can be a mismatch.

2 - Can have duplicate reports

4 - Multiple calls for an export can be blocking at scale if they all run on the same event loop and thread.

3 - The same consecutive update, will be considered as 2 different revisions. Depending on desired implementation if this is by design or not.

1 -  GET request is modifying application state i.e. the view count.

### Issue 2:

- view_counts not deleted when report is deleted

#### Check:

- curl http://127.0.0.1:8000/reports/2                  # bump view count on report 2
    - {"id":2,"title":"US Partner Compensation","firm_id":2,"revisions":["v1"],"views":1}
- curl -X DELETE http://127.0.0.1:8000/reports/2         # delete the highest-id report

curl -X POST http://127.0.0.1:8000/reports   -H "Content-Type: application/json"   -d '{"title": "New Report", "firm_id": 1}'           # gets id=2 again (max+1 reuse)
  - {"id":2,"title":"New Report","firm_id":1,"revisions":["v1"]}

- curl http://127.0.0.1:8000/reports/2                   # views shows stale count from deleted report
    - {"id":2,"title":"New Report","firm_id":1,"revisions":["v1"],"views":2}

#### Fix:

- Before @router.delete("/{report_id}", status_code=204)
  def delete_report(report_id: int):
      report = get_report_or_404(report_id)
      REPORTS.remove(report)
      return
- Add this to the function:
- `_view_counts.pop(report_id, None)`
-  ` @router.delete("/{report_id}", status_code=204)   `
- `def delete_report(report_id: int):       `
- `	report = get_report_or_404(report_id)       `
- `	REPORTS.remove(report)       `
- `	_view_counts.pop(report_id, None)       `
- `	return   `


Contract Ownership

```
API contract
A contract is a definition of how to communicate with an API. The methods, 
The contract is what counts as the same request
how long the answer stays valid
what a caller gets when their retry lands while the first attempt is still running
and which failures are worth remembering.
Includes : Paths, Methods (GET-PUT-POST-DELETE (QUERY new)), Response Shape, Status Codes

Time to respond, Latency not part of contract usually if it is not mission critical
Performance can appear in contract if it is part of contract SLA 

Breaking change
A breaking change is any modification to an API that causes existing client code
to fail or behave differently without the client updating their code. 
**Changes that would cause the code to break on client side**

API versioning (/v1/, /v2/)
Track the API versions via the API paths. Good to run multiple versions of an API, to allow the client to update their code to interact with the API

Swagger / OpenAPI
Documenting APIs and Testing APIs
OpenAPI - Standard for documenting APIs
Swagger - Tools that use OpenAPI to visualize APIs, Generate interactive docs, test endpoints and generate client libraries
Good for testing the APIs.


Backward compatibility
The new API should be able to work with clients built for the old version, without requiring clients to change their code.
Two different APIs should be able to be used with the same client.
```

*
