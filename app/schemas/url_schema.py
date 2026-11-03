from pydantic import BaseModel, HttpUrl

class LinkCreate(BaseModel):
    given_url: HttpUrl

class LinkResponse(BaseModel):
    given_url : str
    short_url : str
    short_code : str