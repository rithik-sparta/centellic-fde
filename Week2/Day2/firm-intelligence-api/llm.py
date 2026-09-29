# how we call the model... nothing in here knows about FASTAPI

import os

import anthropic
from anthropic.types import TextBlock
from pydantic import BaseModel, Field

MODEL = "claude-haiku-4-5-20251001" 


# the SDK defaults are max_retries = 2 and a 600 second read timeout
# both are overriden here delierately ... they are our decsions rather than an accident

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    timeout=30.0,
    max_retries=3,
)

# The prompt and where 
# RULES GO IN SYSTEM
# DATA GOES IN USER

SYSTEM_PROMPT = (
    "You are a legal market analyst writing for an institutional audinece. "
    "Use British English. Use only the figures given to you. "
    "Never invent numbers, rankings or facts that are not in the data provided."
)


def build_prompt(firm: dict) -> str:
    return (
        f"Summarize this law firm in two short paragraphs.\n\n"
        f"Name: {firm['name']}\n"
        f"Jurisdiction: {firm['jurisdiction']}\n"
        f"Revenue: {firm['revenue_usd_m']}\n"
        f"Lawyers: {firm['lawyers']}\n"
        f"Equality Partners: {firm['equity_partners']}\n"
    )

# The call
def summarise_firm(firm: dict) -> dict:
    # one LLM call that returns the text plus what it costs to get it.
    response = client.messages.create(
        model = MODEL,
        max_tokens = 400,
        system = SYSTEM_PROMPT,
        messages = [{"role":"user","content": build_prompt(firm)}]
    )
    text_content = next(
        (block.text for block in response.content if isinstance(block, TextBlock)),
        ""
    )
    
    return {
        "id": firm["id"],
        "name": firm["name"],
        "summary": text_content,
        "input_tokens":response.usage.input_tokens,
        "output_tokens":response.usage.output_tokens,
        "stop_reason":response.stop_reason
    }
    
def estimate_input_tokens(firm: dict) -> int:
    """Count tokens BEFORE sending, Costs nothing, tells you what a call will cost"""
    
    counted = client.messages.count_tokens(
        model = MODEL,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user","content": build_prompt(firm)}],
        
    )
    return counted.input_tokens

def stream_firm_summary(firm: dict):
    """Yields tect chunks as they arrive, rather than waiting for the whole response"""
    
    with client.messages.stream(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user","content": build_prompt(firm)}]
    ) as stream:
        yield from stream.text_stream
        # for text in stream.text_stream:
        #     yield text

class FirmAnalysis(BaseModel):
    """This is the shape we require back... it is not a suggestion to the model.... it is a contract"""
    tier : str = Field(description="One of: magic circle, national, boutique")
    strengths : list[str] = Field(max_length = 3, description = "Strengths associates with the firm")
    risks : list[str] = Field(max_length = 3, description = "Risks associated with the firm")
    headcount_efficiency : str = Field(description = "high, medium or low")


def analyse_firm(firm: dict) -> dict:
    """Structured output. The response is validated against FirmAnalysis or it fails."""
    response = client.messages.parse(
        model = MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user", "content": build_prompt(firm)}],
        output_format = FirmAnalysis
    )
    
    analysis : dict = response.content[0].parsed_output  # type: ignore
    return {
        "id" : firm["id"],
        "name" : firm["name"],
        "analysis" : analysis,
        "input tokens" : response.usage.input_tokens,
        "output tokens" : response.usage.output_tokens,
        "stop reason" : response.stop_reason,
    }
    
    
# Add the generation step
# Retrieval finds documents... RAG's third letter is generate - turn those documents into an answer

GROUNDED_SYSTEM_PROMPT = (
    "You are a legal market analyst, Answer using ONLY the context provided"
    "Cite the document id in square brackets after each claim, like [doc-001]."
    "If the context does not contain the answer, say ecaxtly: "
    "'The provided documents do not answer that question.'"
    "Never use knowledge from outside the context. Use British English. No em dash characters."
)

# Notice where context goes
# Rules in system
# data in user
def answer_from_context(question: str, context: str) -> dict:
    """Answer strictly from retrieved context... The G part of RAG - Generating an answer."""
    response = client.messages.create(
        model = MODEL,
        max_tokens = 500,
        system = GROUNDED_SYSTEM_PROMPT,
        messages = [{
            "role":"user",
            "content" : f"Context: \n\n{context}\n\nQuestion: {question}"
        }],
    )
    
    return {
        "answer" : response.content[0].text, # type: ignore
        "input_tokens" : response.usage.input_tokens,
        "output_tokens" : response.usage.output_tokens,
        "stop_reason" : response.stop_reason
    }
    


