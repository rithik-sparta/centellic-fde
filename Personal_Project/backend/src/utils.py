import re
from datetime import date, datetime
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from pydantic import AfterValidator, BaseModel, BeforeValidator, Field


class Question(BaseModel):
    question : str = Field(min_length=3)
    top_k : int = Field(default=3, gt=0, le=8)
    
_DD_MM_YYYY = re.compile(r"\d{2}-\d{2}-\d{4}")
TIME_ZONE = ZoneInfo(key="Europe/London")

def parse_dd_mm_yyyy(value : Any) -> Any:
    if not isinstance(value, str):
        return value  # let pydantic handle dates / other types
    if not _DD_MM_YYYY.fullmatch(value):
        raise ValueError("date must be in dd-mm-yyyy format")
    try:
        return datetime.strptime(value, "%d-%m-%Y").astimezone(tz=TIME_ZONE).date()
    except ValueError:
        raise ValueError("date is not a valid calendar date")

def not_in_future(value: date) -> date:
    if value > datetime.now(tz=TIME_ZONE).date():
        raise ValueError("date must be today or earlier")
    return value

# Type for dates in format dd-mm-yyy
ddmmyyyyDate = Annotated[date, BeforeValidator(parse_dd_mm_yyyy)]

# Ensure date is of today or before
TodayOrEarlier = Annotated[date, BeforeValidator(parse_dd_mm_yyyy), AfterValidator(not_in_future)]

# helper function to generate a new id
def _create_new_id(entity_records, id_key, prefix):
    new_val = 0
    for entity in entity_records:
        id_value = int(entity[id_key][len(prefix)+1:])
        if new_val <= id_value:
            id_value = new_val + 1
    if id_value < 10:
        return f"{prefix}-0{id_value}"
    else:
        return f"{prefix}-{id_value}"
    

def list_fields(results : dict, fields : list[str]) -> str:
    output = ""
    for field in fields:
        if field in results:
            output += f"'{field}' : {results[field],}\n"
    return output

def list_all_data(entity_name : str, entity_id_name : str, result_collection : list[dict], fields : list[str]) -> str:
    output = ""
    for result in result_collection:
        output += f"{entity_name}: {result[entity_id_name]}\n"
        output += list_fields(result, fields)
        output += "\n"
    return output

def _delete_helper(records: list[dict], borrower_id : str) -> None:
    to_delete = [record for record in records if record["borrower_id"] == borrower_id]
    for record in to_delete:
        records.remove(record)
    

