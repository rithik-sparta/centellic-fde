from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from data import PEOPLE

router = APIRouter(prefix="/people",tags=["prefix"])


class NewPerson(BaseModel):
    name : str = Field(min_length=1)
    role : str = Field(min_length=1)
    firm_id : int
    
def get_person_or_404(person_id: int):
    for person in PEOPLE:
        if person["id"] == person_id:
            return person
    raise HTTPException(status_code=404, detail=f"No person with id {person_id}.")

@router.get("")
def list_people(firm_id: int | None = None):
    if firm_id is None:
        return PEOPLE
    return [person for person in PEOPLE if person["firm_id"] == firm_id]


# get_person
@router.get("/{person_id}")
def get_person(person: dict = Depends(get_person_or_404)):  # noqa: B008
    return person


# add_person
@router.post("", status_code=201)
def add_person(new : NewPerson):
    get_person_or_404(new.firm_id) # ph
    new_id = max(person["id"] for person in PEOPLE) + 1
    person = {
        "id" : new_id,
        "name" : new.name,
        "role": new.role,
        "firm_id": new.firm_id, 
    }
    PEOPLE.append(person)
    return person
