
from typing import cast

from pydantic import BaseModel, Field
from config import MODEL
from agent.model import AGENT_SYSTEM_PROMPT, SYSTEM_PROMPT, TOOLS, _execute_tool, client
from anthropic.types import MessageParam, ToolUnionParam
from agent.summarise_borrower import build_prompt
from utils import list_fields

class BorrowerAnalysis(BaseModel):
    """This is the shape we require back... it is not a suggestion to the model.... it is a contract"""
    tier : str = Field(description="One of: magic circle, national, boutique")
    strengths : list[str] = Field(max_length = 3, description = "Strengths associates with the borrower")
    risks : list[str] = Field(max_length = 3, description = "Risks associated with the borrower")
    headcount_efficiency : str = Field(description = "high, medium or low")
    
    
    rating : str = Field(description="The credit rating of the borrower.")
    sector : str = Field(description="The sector the borrower works in.")
    leverage : str = Field(description="The leverage of the borrower.")
    interest_cover : str = Field(description="The interest cover of the borrower")
    risk_of_default : str = Field(description="High, medium or low")
    points_to_note : list[str] = Field(max_length=4, description="Points of importance about the borrower that should be taken into account when making a credit rating.")
    
def analyse_borrower(borrower: dict) -> dict:
    """Structured output. The response is validated against BorrowerAnalysis or it fails."""
    response = client.messages.parse(
        model = MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role":"user", "content": build_prompt(borrower)}],
        output_format = BorrowerAnalysis
    )

    analysis : dict = response.content[0].parsed_output  # type: ignore
    
    return {
        "id" : borrower["borrower_id"],
        "name" : borrower["name"],
        "analysis" : analysis,
        "input tokens" : response.usage.input_tokens,
        "output tokens" : response.usage.output_tokens,
        "stop reason" : response.stop_reason,
    }
    
    
class CreditAssessment(BaseModel):
    strengths : list[str] =  Field(max_length=3, description="List of strengths from the borrowers credit assessment. Each point is at most 2 sentences.")
    risks : list[str] = Field(max_length=3, description="List of risks from the borrowers credit assessment, that are holding their credit rating back. Each point is at most 2 sentences.")
    proposed_internal_rating : int = Field(gt=0 ,lt=23, description="The proposed internal rating of the borrower from 1 to 22.")
    rationale : str =  Field(description="A small 4 sentence maximum paragraph reasoning behind the proposed rating given.")
    
def build_credit_assessment_prompt(borrower : dict):
    prompt = "Give a credit assessment for the following borrower. Include details about their strengths, risks, a proposed internal rating from 1 (best) to 22 (worst) and a rationale behind the chosen rating. Be detailed but brief in detailing strengths, risks and rationale."
    prompt += list_fields(borrower,["borrower_id","name","sector","latest_period_id"])
    return prompt
    
    
MAX_ITERATIONS = 15
def credit_assessment(borrower : dict) -> dict:
    """Run the tool-use loop until the model answers, orrrr the limit is hit"""
    messages : list[MessageParam] = [{"role": "user", "content": build_credit_assessment_prompt(borrower)}]
    total_input_tokens = 0
    total_output_tokens = 0
    tool_calls_made = 0
    tool_count : dict[str,int] = {}

    # the loop
    for _ in range(MAX_ITERATIONS):
        response = client.messages.parse(
                model = MODEL,
                max_tokens=500,
                system=AGENT_SYSTEM_PROMPT,
                tools=cast(list[ToolUnionParam], list(TOOLS.values())),
                messages=messages,
                output_format = CreditAssessment
            )

        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        # checking whether the model is done
        # Always the case we will reach a point where tool_use is not a tool_use
        if response.stop_reason != "tool_use":
            assessment = next(
                (
                    block.parsed_output
                    for block in response.content
                    if block.type == "text" and block.parsed_output is not None
                ),
                None,
            )
            if assessment is None:
                raise RuntimeError(
                    "Model response completed without a parsed credit assessment "
                    f"(stop_reason={response.stop_reason!r})"
                )
            print(tool_count)
            return {
                "output": assessment,
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
                tool_count[tool_block.name] = tool_count.get(tool_block.name, 0)+1
            else:
                print(is_error, result_text)
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
        "output": None,
        "completed" : False,
        "tool_calls_made": tool_calls_made,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "stop_reason": response.stop_reason,

    }