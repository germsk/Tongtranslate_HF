from pydantic import BaseModel
from typing import List, Optional

#for ensuring output is json format
class Entity(BaseModel):
    entity_id: int
    chinese: str
    english: Optional[str] = None
    type: str
    context_phrase: str
    region: str
    pinyin: Optional[str] = None

class EntityList(BaseModel):
    entities: List[Entity]
