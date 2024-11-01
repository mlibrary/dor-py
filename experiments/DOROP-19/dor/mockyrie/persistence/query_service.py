from dataclasses import dataclass, field

from .resource import Resource

from sqlalchemy import select, func, cast
from sqlalchemy.dialects.postgresql import JSONB, JSONPATH
from sqlalchemy.sql import text

@dataclass
class QueryService:
    adapter: "MetadataAdapter"

    def find_all(self):
        stmt = select(Resource)
        rows = self.adapter.session.execute(stmt).all()
        resources = []
        for row in rows:
            resources.append(self.adapter.resource_factory.to_resource(row[0]))
        return resources

    def find_by(self, id: int):
        stmt = select(Resource).where(Resource.id==id)
        row = self.adapter.session.execute(stmt).one()[0]
        return self.adapter.resource_factory.to_resource(row)

    def find_by_alternate_identifier(self, alternate_identifier: str):
        # oh now we get something interesting
        stmt = select(Resource).where(
            Resource.data['alternate_ids'].op('@>')(
                cast([{"id": alternate_identifier}], JSONB)
            )
        )
        row = self.adapter.session.execute(stmt).one()[0]
        return self.adapter.resource_factory.to_resource(row)

    # valkyrie can take a model class as an second option, e.g. filtering
    # by the member class
    # it would be nice to get the cast of
    # (b.member->>'id')::integer from Resource but so far inspecting
    # via sqlalchemy only yields an instance of sqlalchemy.sql.sqltypes.Integer
    def find_members(self, resource=None):
        id_column_type = self.adapter.get_column_type(Resource.id)
        stmt = text(f"""
                    SELECT member.* FROM mock_resource a,
                    jsonb_array_elements(a.data->'member_ids') WITH ORDINALITY AS b(member, member_pos)
                    JOIN {Resource.__table__.name} member ON (b.member->>'id')::{id_column_type} = member.id WHERE a.id = :id
                    ORDER BY b.member_pos""")

        return map(self.adapter.resource_factory.to_resource,
                   self.adapter.session.execute(stmt, { "id": resource.id} ).all())
