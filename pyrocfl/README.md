# pyrocfl - Python API to rocfl

## Description

The `pyrocfl` crate provides Python bindings for the `umich` branch of the [library fork](https://github.com/mlibrary/rocfl) of `rocfl`.

The docker image builds and installs both the `rocfl` executable and library by downloading the `rust` source from the `umich` branch of the library fork of `rocfl`.

Since the `rocfl` executable and library are always in sync the `ocfl_repository_gateway` can be implemented using both. The end goal would to replace all the `subprocess` calls to the `rocfl` executable with calls to the `pyrocfl` API as illustrated below.

```python
    def create_repository(self) -> None:
        init_fs_repo(root=str(self.storage_path), layout=str(self.storage_layout.value))
        # args = [
        #     "rocfl", "-r", self.storage_path, "init",
        #     "-l", self.storage_layout.value
        # ]
        # try:
        #     subprocess.run(args, check=True, capture_output=True)
        # except CalledProcessError as e:
        #     raise RepositoryGatewayError() from e
```
## Development 

### rocfl Development

1. Merge changes to the `umich` branch of the library fork of `rocfl`.
2. Rebuild the docker container.
```commandline
docker compose down
docker compose build --no-cache
docker compose up -d
```
3. Proceed to [pyrocfl Development](#pyrocfl-development)

### pyrocfl Development

In the **app** container, `docker compose exec -- app bash`, use `poetry shell` to enable the **python** virtual environment.

1. Create and or modify tests in the `tests` directory e.g...
```commandline
vi tests/test_pyrocfl.py
```
2. Make any necessary changes to the `ocfl_repository_gateway` module.
```commandline
vi gateway/ocfl_repository_gateway.py
```
3. Make any necessary changes to the `pyrocfl` library.
```commandline
vi pyrocfl/src/lib.rs
```
4. Build and install the `pyrocfl`library.
```commandline
python -m rustimport build
```
5. Run tests.
```commandline
pytest
```
6. Repeat steps 2-5 until tests pass.
7. Proceed to [rocfl Development](#rocfl-development)

## References

- [How I Design And Develop Real-World Python Extensions In Rust](https://medium.com/@kudryavtsev_ia/how-i-design-and-develop-real-world-python-extensions-in-rust-2abfe2377182)
- [rustimport - Import Rust directly from Python!](https://github.com/mityax/rustimport)
- [PyO3](https://github.com/PyO3/pyo3)
- [The Rust Programming Language, 2nd Edition](https://learning.oreilly.com/library/view/the-rust-programming/9781098156817)
