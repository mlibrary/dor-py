# dor-py

Python code for the DOR project.

## Setup

1. Clone the repo

```
git clone https://github.com/mlibrary/dor-py.git
cd dor-py
```

2. In the terminal, run the `init.sh` 
```
./init.sh
```
This will:

* set up the initial environment variables file
* build the docker image
* install the python dependencies

`./init.sh` can be run more than once. 
  
1. Edit `.env` with actual environment variables

2. In the app container, use `poetry shell` to enable the virtual environment. Otherwise use:
```
 docker compose run --rm app poetry run YOUR_COMMAND
```

## Generating Samples

To generate sample packages, on the command line run:

```
docker compose run --rm app poetry run dor samples generate --collid xyzzy --num-scans 5 --total 1 --versions 1
```

This will generate a submission package in BagIt format for the collection `xyzzy` for one item made up of 5 page scans.

The complete list of options:

```
--collid: str -- required
--action: store|stage|purge
--num_scans: int = None -- if unspecified, a random number of scans will be generated
--total: int = 1 -- number of items to generate
--versions: int = 1 --- number of versions to generate
--output_pathname: str -- default is the "output" directory at the root of this repository
```

**How does the `versions` option work?** The first version of the item will contain all the scans. 
The next versions will only contain a random subset of updated scans.

**Can you validate the METS2 documents?** The schemas for METS2 and PREMIS3 are in the `etc/xsd` 
directory. With `xmllint --schema` you can only use _one_ of these schemas, so validating a METS2
document will always complain about the `PREMIS:object` type.
