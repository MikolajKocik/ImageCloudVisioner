from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ImageInsights(BaseModel):
    analysis: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)