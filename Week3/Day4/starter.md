Plain search terms, nothing to read in depth. Just get a rough sense of each one before we build it properly.

1. **"Tool use" or "function calling" for an LLM** - both phrases mean roughly the same thing, different providers use different names for it. What is it, in plain terms?
   1. The tools that an LLM has the ability to interact with.
   2. way of letting an LLM  **ask your code to do something** , instead of just generating text.
   3. Tools/Externsions - Google (Gemini)
   4. Allows your LLM to interact with external tools, in order to get data to answer prompts.
2. **"AI agent"** - you've probably heard the term already. What do people actually mean by it?
   1. An LLM Model that acts autonomously in a non pre determined seqeunce of steps.
   2. It has access to a number of tools, other than generating text. It can take actions as well as observe and adjust its approach based on changes to its environment or new information
   3. Combination of LLMs, tools, MCPs that create an AI agent capable of complex tasks.
   4. Agent harness + LLM - Handles permissions, loops, context, memory, data gathering, state management. LLM alone can't use tools
   5. Capable of finding answers by itself (Autonomy)
   6. How to control the agent:
      1. Evaluation Harness - Can restrict the model from infinite loops
      2. Other agents can evaluate the work of an agent.
      3. Human in the loop
   7. How agents escape harnesses:
      1. Harnesses built around security packages.
      2. Agents learn themselves.
      3. Usually done through dependencies that was not properly maintained. AI agent is trained on large corpuses of data, including code, and github issues of bugs.
3. **Streamlit** - what is it, and what's it normally used for?
   1. A python frameowrk for quickly prototyping basic web app UIs in Python.
   2. For when you have some functionality in python scripts that you want to quickly prototype.
   3. Don't need to know frontend development (no HTML, CSS, JavaScript). Only python.
   4.
