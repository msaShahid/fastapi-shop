from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
 
    name: str = Field(min_length=1, max_length=100, examples=["Wireless Mouse"])
    price_cents: int = Field(gt=0, description="Price in cents, always a positive integer")


class ItemRead(BaseModel):

    id: int
    name: str
    price_cents: int

class ItemPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price_cents: int | None = Field(default=None, gt=0)
