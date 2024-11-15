// rustimport:pyo3

use pyo3::prelude::*;

#[pyfunction]
fn say_hello() {
    println!("Hello from pyrocfl, implemented in Rust!")
}

// Uncomment the below to implement custom pyo3 binding code. Otherwise, 
// rustimport will generate it for you for all functions annotated with
// #[pyfunction] and all structs annotated with #[pyclass].
//
//#[pymodule]
//fn pyrocfl(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
//    m.add_function(wrap_pyfunction!(say_hello, m)?)?;
//    Ok(())
//}

#[pyclass]
struct Number(i32);

#[pymethods]
impl Number {
    #[new]
    fn new(value: i32) -> Self {
        Self(value)
    }

    // For `__repr__` we want to return a string that Python code could use to recreate
    // the `Number`, like `Number(5)` for example.
    fn __repr__(&self) -> String {
        // We use the `format!` macro to create a string. Its first argument is a
        // format string, followed by any number of parameters which replace the
        // `{}`'s in the format string.
        //
        //                       👇 Tuple field access in Rust uses a dot
        format!("Number({})", self.0)
    }
    // `__str__` is generally used to create an "informal" representation, so we
    // just forward to `i32`'s `ToString` trait implementation to print a bare number.
    fn __str__(&self) -> String {
        self.0.to_string()
    }
}


// Error propagation traits
use pyo3::exceptions::PyValueError;
use rocfl::ocfl::RocflError;
use pyo3::PyErr;

pub struct PyRocflError(RocflError);

impl From<PyRocflError> for PyErr {
    fn from(error: PyRocflError) -> Self {
        PyValueError::new_err(error.0.to_string())
    }
}

impl From<RocflError> for PyRocflError {
    fn from(error: RocflError) -> Self {
        Self(error)
    }
}

fn raise_rocfl_error() -> Result<(), RocflError> {
    Err(RocflError::General("rocfl error".to_string()))
}

#[pyfunction]
pub fn propagate_rocfl_error() -> Result<(), PyRocflError> {
    raise_rocfl_error()?;
    Ok(())
}

use rocfl::ocfl::LayoutExtensionName;
use rocfl::ocfl::OcflRepo;
use std::path::Path;
use rocfl::ocfl::{SpecVersion, StorageLayout};

#[pyclass]
pub enum PyStorageLayout {
    FlatDirect,
    HashedNTuple,
}

#[pyfunction]
pub fn init_fs_repo(root: &str, layout: &str) -> PyResult<()>  {
    //         config.root.as_ref().unwrap(),
    //         config.staging_root.as_ref().map(Path::new),
    //         spec_version,
    //         create_layout(cmd.layout, cmd.config_file.as_deref())?,

    let my_root = root;
//    let my_staging_root: Option<&Path> = Some(Path::new(staging_root));
    let my_staging_root: Option<&Path> = None;
//     let my_spec_version_a: Result<SpecVersion, RocflError> = SpecVersion::try_from_num(spec_version);
//     let my_spec_version: SpecVersion = match my_spec_version_a {
//         Ok(v) => v,
//         Err(e) => return Err(PyValueError::new_err(e.to_string())),
//     };

    let my_spec_version: SpecVersion = SpecVersion::Ocfl1_1;

    let my_layout_name = match layout {
        "0002-flat-direct-storage-layout" => LayoutExtensionName::FlatDirectLayout,
        "0004-hashed-n-tuple-storage-layout" => LayoutExtensionName::HashedNTupleLayout,
        _ => return Err(PyValueError::new_err("layout must be one of 0002-flat-direct-storage-layout or 0004-hashed-n-tuple-storage-layout")),
    };
    let my_layout_a: Result<StorageLayout, RocflError> = StorageLayout::new(my_layout_name, None);
    let my_layout_b: StorageLayout = match my_layout_a {
        Ok(v) => v,
        Err(e) => return Err(PyValueError::new_err(e.to_string())),
    };
    let my_layout: Option<StorageLayout> = Some(my_layout_b);

// Initializes a new `OcflRepo` instance backed by the local filesystem. The OCFL repository
// most not already exist.
//     pub fn init_fs_repo(
//         storage_root: impl AsRef<Path>,
//         staging: Option<&Path>,
//         version: SpecVersion,
//         layout: Option<StorageLayout>,
//     ) -> Result<Self>

    let repo: Result<OcflRepo, RocflError> = OcflRepo::init_fs_repo(
           my_root,
           my_staging_root,
           my_spec_version,
           my_layout,
    );

    let _ = match repo {
        Ok(v) => v,
        Err(e) => return Err(PyValueError::new_err(e.to_string())),
    };

    Ok(())
}
