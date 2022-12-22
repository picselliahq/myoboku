from ninja import Schema


class ResourceSchema(Schema):
    nb_gpu: int
    nb_cpu: int


class JobInputSchema(Schema):
    image: str
    resources: ResourceSchema
    env: dict
    volumes: list
