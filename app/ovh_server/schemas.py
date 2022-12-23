from ninja import Schema


class ResourceSchema(Schema):
    cpu: int
    gpu: int


class JobInputSchema(Schema):
    image: str
    resources: ResourceSchema
    env: list
    volumes: list
