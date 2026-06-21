from ninja_schema import Schema


class Error(Schema):
    message: str


class OK(Schema):
    message: str


class InactiveError(Exception):
    pass


class ExistsError(Exception):
    pass


class DeleteError(Exception):
    pass


class SchemaError(Exception):
    pass
