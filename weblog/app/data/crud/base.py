from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from data.database.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateType = TypeVar("CreateType", bound=BaseModel)
UpdateType = TypeVar("UpdateType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateType, UpdateType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db: Session, *, obj_in: CreateType) -> ModelType:
        db_object = self.model(**jsonable_encoder(obj_in))

        db.add(db_object)
        db.commit()
        db.refresh(db_object)

        return db_object

    def read(self, db: Session, requested_id: Any) -> Optional[ModelType]:
        return db.query(self.model). \
            filter(self.model.id == requested_id). \
            first()

    def read_many(self, db: Session, *, is_limit: bool = False, limit: int = 100) -> List[ModelType]:
        if is_limit:
            return db.query(self.model). \
                order_by(self.model.id). \
                limit(limit). \
                all()

        return db.query(self.model). \
            order_by(self.model.id). \
            all()

    # TODO implementation
    def update(self, db: Session, *,
               db_object: ModelType,
               obj_in: Union[UpdateType, Dict[str, Any]]) -> ModelType:

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        db_object_data = jsonable_encoder(db_object)
        for field in db_object_data:
            if field in update_data:
                db_object.field = update_data[field]
                # setattr(db_obj, field, update_data[field])

        db.add(db_object)
        db.commit()
        db.refresh(db_object)

        return db_object

    # TODO delete
