Task 2:

* Why
  * If customers raise the same problem many times, the support team can get overwhelmed dealing with redundant tickets. We need to ensure that we can merge the same ticket all the time.
* What
  * Two tickets are identified as identical if they both:

    * Have the same customer field.
    * Have the same message. Should be case insensitive comparison.
  * If two tickets are identical

    * Close the newer ticket (identified by the created_at field), unless the newer ticket is of an Urgent priority while the oldest Ticket is not, then make the older ticket refer to the newer ticket, closing the older ticket.
    * Put a reference to the older ticket in the newer ticket. The default value of this field should be None. If this is the third or greater ticket that is the same, we assign the reference to the oldest ticket in the ticket reference chain.
* Context
  * tickets.py
  * README.md
* Constraints
  * No AI system that checks tickets are identical.
  * Do not add or remove or change library versions
* Tasks
  * Add a reference field to the Ticket class.
  * Add a comparison for two tickets checking the customer field and message.
  * If two tickets are identical, merge them according to the strategy described under **What.**
* Done
  * Test behaviour using tickets.py
