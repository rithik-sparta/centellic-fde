import llm
from data import FIRMS

response = llm.summarise_firm(FIRMS[0])
print(response)