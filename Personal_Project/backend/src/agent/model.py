# File to hold information about models, tools and prompts used.
from collections.abc import Callable
from typing import cast

import anthropic
from anthropic.types import MessageParam, ToolUnionParam
from config import ANTHROPIC_API_KEY, MODEL

from agent.tools import CalculationTool, DocumentSearchTool, RecordSearchTool

SYSTEM_PROMPT = (
    "You are a credit analyst reviewing a borrowers performance. "
    "Use British English. Use only the data given to you. "
    "Do not make calculations yourself, only rely on the data and tools provided."
)

GROUNDED_SYSTEM_PROMPT = (
    "You are a credit analyst, Answer using ONLY the context provided"
    "Cite the document id in square brackets after each claim, like [doc-01]."
    "If the context does not contain the answer, say exactly: "
    "'The provided documents do not answer that question.'"
    "Never use knowledge from outside the context. Use British English. No em dash characters."
)

AGENT_SYSTEM_PROMPT = (
    "You are credit analyst with access to tools to assess a borrowers credit rating. Use the tool whenever a question needs "
    "information you don't already have - do not guess. Cite the document id in square brackets after each claim, like [doc-01]."
    "If the context does not contain the answer, say exactly:"
    "'The provided documents do not answer that question.'"
    "Use the right tool for the job:"
    "(1) search_document_store to find relevant documents for a question."
    "(2) search_records to search relevant records to assess a borrower."
    "(3) calculation_tool to perform calculations using the data."
)

TOOLS : dict[str,dict] = {
    "search_document_store" : DocumentSearchTool.schema(),
    "search_records" : RecordSearchTool.schema(),
    "run_calculation" : CalculationTool.schema() 
}


client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    timeout=30.0,
    max_retries=3,
)

def estimate_input_tokens(borrower: dict, model : str, system_prompt : str, prompt_builder : Callable[[dict],str]) -> int:
    """Count tokens BEFORE sending, Costs nothing, tells you what a call will cost"""

    counted = client.messages.count_tokens(
        model = model,
        system = system_prompt,
        messages=[{"role":"user","content": prompt_builder(borrower)}],

    )
    return counted.input_tokens

def answer_from_context(question: str, context: str) -> dict:
    """Answer strictly from retrieved context... The G part of RAG - Generating an answer."""
    response = client.messages.create(
        model = MODEL,
        max_tokens = 500,
        system = GROUNDED_SYSTEM_PROMPT,
        messages = [{
            "role" : "user",
            "content" : f"Context: \n\n{context}\n\nQuestion: {question}"
        }],
    )
    
    return {
        "answer" : response.content[0].text, # type: ignore
        "input_tokens" : response.usage.input_tokens,
        "output_tokens" : response.usage.output_tokens,
        "stop_reason" : response.stop_reason
    }


# the loop - one call, check, maybe repeat
MAX_ITERATIONS = 4
def ask_with_tools(question: str) -> dict:
    """Run the tool-use loop until the model answers, orrrr the limit is hit"""
    messages : list[MessageParam] = [{"role": "user", "content": question}]
    total_input_tokens = 0
    total_output_tokens = 0
    tool_calls_made = 0

    # the loop
    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=AGENT_SYSTEM_PROMPT,
            tools=cast(list[ToolUnionParam], [TOOLS]),
            messages=messages,
        )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # checking whether the model is done
        # Always the case we will reach a point where tool_use is not a tool_use
        if response.stop_reason != "tool_use":
            final_text = next((b.text for b in response.content if b.type == "text"), "")
            return {
                "answer": final_text,
                "completed": True,
                "tool_calls_made": tool_calls_made,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "stop_reason": response.stop_reason,
            }

        # indent
        # response content - when added to messages per round
        tool_blocks = [b for b in response.content if b.type == "tool_use"]
        tool_results : list = []
        messages.append({"role" : "assistant", "content" : response.content})
        for tool_block in tool_blocks:
            result_text, is_error = _execute_tool(tool_block.name, tool_block.input)
            if not is_error:
                tool_calls_made += 1
            tool_results.append({
                "type" : "tool_result",
                "tool_use_id" : tool_block.id,
                "content" : result_text,
                "is_error" : is_error
            })

        messages.append({"role" : "user",
                        "content" : tool_results
        })

    return {
        "answer": "",
        "completed" : False,
        "tool_calls_made": tool_calls_made,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "stop_reason": response.stop_reason,

    }

def _execute_tool(name: str, tool_input: dict) -> tuple[str,bool]:
    """Run the requested tool. Returns (result_text, is_error)"""

    # Guard 1 - we only have 1 real tool, checking it is equal to that
    if name not in TOOLS:
        return f"Unknown tool: {name}", True
    
    if name == "search_document_store":
        # Guard 2 - Even the right tool is usesless without its one argument. If we do not have a query, how does the agent know what to answer?
        if "query" not in tool_input:
            return 'Error: missing required field "query"', True
        
        result_text, is_error = DocumentSearchTool.get_context(tool_input["query"])
        
        return result_text, is_error
    
    elif name == "search_records":
        if "entity_name" not in tool_input:
            return 'Error, missing required field "entity_name"', True
        result_text, is_error = RecordSearchTool.get_records(tool_input["entity_name"],tool_input["borrower_id"])
        return result_text, is_error
    elif name == "calculation_tool":
        if "name" not in tool_input:
            return 'Error: missing required field "name"', True
        if "arguments" not in tool_input:
            return 'Error: missing required field "argument"', True
        result_text, is_error = CalculationTool.run(tool_input["name"], tool_input["arguments"])
        return result_text, is_error
    else:
        return f'Error: Unknown tool "{name}"', True