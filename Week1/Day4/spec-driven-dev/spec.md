Task 1:

* **Why**

  * When a ticket misses its first response target it needs to be acknowledged and prioritised.
* **What**

  * Add an assigned_to field to the Ticket class that states who is responsible for this ticket.
  * If a ticket exceeds the response target (no reply within 5 days. )
    * Set the ticket type to urgent
    * Assign to a senior member
  * Closed tickets should be ignored, no matter the priority type
* **Context**

  * ticket.py
  * README.md
* **Constraints**

  * Do not send emails to those who it is being reassigned to
  * Only create a list of the affected tickets
  * Do not create a class to represent colleagues.
  * Do not create new Tickets based on the original, modify the fields themselves.
  * No new libraries
* **Tasks**

  1. Add a field assigned_to to Tickets
  2. If the ticket is closed already, we skip that particular ticket.
  3. If a ticket exceeds its response target of 5 days
     * Assign to a senior member of the team
     * Set the type of ticket to urgent
* **Done**

  * Test the feature against load_sample_tickets, ensure we get the behvaiour specified under the **What** section.
