APIs From Both Sides

* **A client that silently returns partial data makes every downstream conclusion wrong. The downstream code has no way to know.**
  * **If there is no reactive code, cascading failures can be hard to debug**
* API
  * Definition: An API is a set of rules or protocols that enable software applications to communicate with each other to exchange data, common features and functionality.
  * Role in SDLC/ Full Stack Application:
    * Implementation: To integrate API functionality into an existing application
  * Design Patterns:
    * versioning
    * layered pattterns - Create application in different layers, business logic, database query layer, output format layer
    * repo pattern, mvc pattern, csr
    * Exist to make code maintainable and scalable
  * Frameworks:
    * Django, Flask, FastAPI
    * Tools to build APIs
  * Questions:
    * How do we test if an API call does what we intend it to do?
      * status codes, responses, Postman to automate api testing
      * Do we know the output of the API?
*
