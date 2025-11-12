from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def __repr__(self):
        __allow_unmapped__ = True  # noqa: F841
        data = {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if "api_key" != c.name
        }
        return f"{self.__class__.__name__}({data})"
