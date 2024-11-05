# DOROP-19 - experimenting with database persistence

**What is this?** A tiny reimplementation of [Valkyrie](https://github.com/samvera/valkyrie/wiki/Dive-into-Valkyrie) built atop [SQLAlchemy](https://www.sqlalchemy.org/) and PostgreSQL [JSONB](https://www.postgresql.org/docs/current/datatype-json.html).

**Why?** This is a demonstration of a Data Mapper pattern. The types of digital objects are represented by [dataclass](https://docs.python.org/3/library/dataclasses.html) classes and are synchronized to the database via a metadata adapter.

*This is not a recommendation for how DOR should be implemented* although I'll confess it just works for me.

This experiment follows Valkyrie naming conventions (more or less), although that does lead to some confusion (the data classes are *resources* but the database table is also a *resource*...)

It's also possibly harder to see how modern SQLAlchemy is different than the usual Active Record pattern. There is a more [explicit mapper pattern](https://docs.sqlalchemy.org/en/13/orm/mapping_styles.html#classical-mappings) available.

## Setup

You've cloned the `dor-py` repo, fetched this branch, and in the terminal, run `init.sh`

```sh
$ cd ./experiments/DOROP-19
$ ./init.sh
```

This will:

* set up the initial environment variables file
* build the docker image
* install the python dependencies
* create the development database

## Quick Overview

```sh
# connect to the app container
$ docker compose run --rm app bash

# set up the database tables
$$ poetry run dor mockyrie setup

# save a monograph; this will also create member assets
$$ poetry run dor mockyrie save-monograph --num-assets 5

# save a monograph with an alernate identifier; we're not doing 
# any checks for the uniqness of alternative identifiers
$$ poetry run dor mockyrie save-monograph --alternate-identifier dlxs:bhl:101 --num-assets 5

# list all resources
$$ poetry run dor mockyrie find-all
<[1] Asset : Compare walk president hear eat.>
<[2] Asset : Up prove fill minute everything affect sea.>
<[3] Asset : Purpose simply bed stay baby human rise.>
<[4] Asset : News free safe relationship discuss last activity share.>
<[5] Asset : Protect know image however police.>
<[6] {dlxs:bhl:102} Monograph : Most something imagine hope kind imagine military.>

# list the members of a monograph
$$ poetry run dor mockyrie find-members 6
∆ find_members <[6] {dlxs:bhl:102} Monograph : Most something imagine hope kind imagine military.>
	- <[1] Asset : Compare walk president hear eat.>
	- <[2] Asset : Up prove fill minute everything affect sea.>
	- <[3] Asset : Purpose simply bed stay baby human rise.>
	- <[4] Asset : News free safe relationship discuss last activity share.>
	- <[5] Asset : Protect know image however police.>

# set an alternate identifier
$$ poetry run dor mockyrie set-alternate-identifier <id> --alternate-identifier <alt-id>

# update a monograph
$$ poetry run dor mockyrie update-monograph 6 --key lang --value en-AU

# dump a resource
$$ poetry run dor mockyrie dump-resource 6
∆ dump_resource <[6] {dlxs:bhl:102} Monograph : Most something imagine hope kind imagine military.>
{
  "id": 6,
  "created_at": "2024-11-05T15:08:44.690644Z",
  "updated_at": "2024-11-05T15:08:44.690644Z",
  "metadata": {
    "common": {
      "lang": "en-AU",
      "title": "Most something imagine hope kind imagine military."
    }
    ...
}
```

## How this works

```
dor
├── cli
│   ├── __init__.py
│   ├── main.py
│   └── mockyrie.py               # commands
├── __init__.py
├── mockyrie
│   ├── models.py                 # domain models
│   └── persistence               # database/repository layer
│       ├── __init__.py
│       ├── metadata_adapter.py   # the metadata adapter is the main repository interface
│       ├── persister.py          # database CRUD (only create/update is impelemented)
│       ├── query_service.py      # database query
│       ├── resource_factory.py   # factory to convert between domain/repository objects
│       └── resource.py           # the sqlalchemy model
└── settings.py
```

How does this get used? A `MetadataAdapter` is instantiated with a reference to the SQLAlchemy session:

```python
# instantiate the adatper
adapter = MetadataAdapter(session=get_session())

# use the query service
resource = adapter.query_service.find_by(id)

# query the data in the JSONB column
resource = adapter.query_service.find_by_alternate_identifier(alternative_id)

# use the persister
resource = adapter.persister.save(resource=resource)

# the resource factory transforms domain objects into ORM objects 
# (from_resource) or the reverse (to_resource)
# e.g.
stmt = select(Resource).where(Resource.id==id)
row = self.adapter.session.execute(stmt).one()[0]
return self.adapter.resource_factory.to_resource(row)

# domain objects are persisted serialized as vanilla Python
# structures before being persisted by SQLAlchemy in the JSONB column:
data = TypeAdapter(resource.__class__).dump_python(resource)
orm_object.data = data

# in the reverse case, the domain object can be instantiated 
# using the parsed JSON structure:
resource = cls(**( orm_object.data )
```

## Questions/Next Steps

- [ ] is this a useful approach for DOR?

- [ ] How are relationship modeled? Both in the domain and storage?
  
- [ ] `mockyrie.persistence.resource_factory.ResourceFactory` is a simplified version [Vaklyrie::Persistence::Postgres::ResourceConvert](https://github.com/samvera/valkyrie/blob/v2.0.0/lib/valkyrie/persistence/postgres/resource_factory.rb) and [Vaklyrie::Persistence::Postgres::ResourceConvert](https://github.com/samvera/valkyrie/blob/v2.0.0/lib/valkyrie/persistence/postgres/resource_converter.rb); the Valyrie versions do some extra work to generate instances vs. plain Ruby hashes/arrays when thawing JSONB 

