* Tautological Test - Test that cannot fail no matter what e.g. True == True

  * A **tautological test** is a unit test that ends up checking the same logic as the code under test (so it can pass even if the code is wrong). It often happens when the test builds its “expected” result using the exact same formula or helper that the production code uses, or when the test assertion is “tautological” because it can’t fail (for example, an “expected” value is the same object as the “actual” value).
* Seam - So tests do not call the model at all. Builds own client, no way to test it without the model.

  * Place in program, where its behaviour can be changed without changing the code itself. Can change the make up of the functions.
  * A seam in software testing is a specific point in the code where you can alter the behavior of a program without changing the source code itself. This allows developers to test different scenarios more easily. Seams enable the introduction of test doubles, such as mocks or stubs, which can simulate various behaviors during testing.
* Boundary - So type checker does not go blind on an untyped reply. json.loads hands back an untyped blob and we index into it and hope the type matches.

  * A boundary, on the other hand, refers to the line between your code and external systems or components that you do not control. This includes third-party APIs, libraries, or other software components. Boundaries define how your software interacts with these external elements, and they can introduce complexities that affect testing.
* Layers - So two suites, asking two different questions. One test case asserts on model prose. e.g. Testing layers of the application
* Make client an argument. Inject into the function
* Protocol : Structural Typing
