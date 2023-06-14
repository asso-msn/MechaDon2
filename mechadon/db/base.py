from sqlalchemy import orm

from mechadon.helpers import str_format


class Base:
    UPDATERS = {}

    @orm.declared_attr
    def __tablename__(cls):
        return f"{str_format.camel_to_snake(cls.__name__)}s"

    def __repr__(self):
        if isinstance(self, type):
            class_ = self
        else:
            class_ = type(self)
        header = [class_.__name__]
        if hasattr(self, "id"):
            header.append(f"#{self.id}")
        body = [
            f"{column.name}={getattr(self, column.name)}"
            for column in class_.__table__.columns
            if column.name != "id"
        ]
        return "<{header}: {body}>".format(
            header=" ".join(header), body=", ".join(body)
        )
