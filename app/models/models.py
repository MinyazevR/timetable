from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint

Base = declarative_base()


class Event(Base):
    """A table representing the Event entity"""
    __tablename__ = "Event"
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    description = Column(String(256))
    location = Column(String(256))
    __table_args__ = (UniqueConstraint('start_time', 'end_time', 'description',
                                       'location'), )


class User(Base):
    """A table representing the teacher entity"""
    __tablename__ = "User"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    middle_name = Column(String(128), nullable=True)
    post = Column(String(128))
    department = Column(String(256))


class UserToEvent(Base):
    """A table for a many-to-many relationship for User and Event entities"""
    __tablename__ = "UserToEvent"
    user_id = Column(Integer,
                     ForeignKey('User.id', ondelete='CASCADE'),
                     primary_key=True)
    # user = relationship('User', back_populates='user_events')
    event_id = Column(Integer,
                      ForeignKey('Event.id', ondelete='CASCADE'),
                      primary_key=True)


class GroupToEvent(Base):
    """A table for a many-to-many relationship for Group and Event entities"""
    __tablename__ = "GroupToEvent"
    group_id = Column(Integer,
                      ForeignKey('Group.id', ondelete='CASCADE'),
                      primary_key=True)
    event_id = Column(Integer,
                      ForeignKey('Event.id', ondelete='CASCADE'),
                      primary_key=True)


class Field(Base):
    """A table representing the Field entity"""
    __tablename__ = "Field"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))


class Group(Base):
    """A table representing the Group entity"""
    __tablename__ = "Group"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    year = Column(Integer)
    type = Column(String(32))
    field_id = Column(Integer, ForeignKey('Field.id', ondelete='CASCADE'))
