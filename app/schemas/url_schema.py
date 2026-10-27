from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    given_url: HttpUrl