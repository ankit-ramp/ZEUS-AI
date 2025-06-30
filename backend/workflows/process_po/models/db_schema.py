from pydantic import BaseModel

class datalake_rq_body(BaseModel):
    datalake_schema: str
    datalake_tbl: str
    entity: str