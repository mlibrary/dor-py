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

///////////////////////////////////////////////////////////////////////////////
//
// Simple tuple struct
//
///////////////////////////////////////////////////////////////////////////////
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

///////////////////////////////////////////////////////////////////////////////
//
// Error propagation traits
//
///////////////////////////////////////////////////////////////////////////////

use pyo3::exceptions::PyValueError;
use rocfl::ocfl::RocflError;
use pyo3::PyErr;

// Using Tuple Structs Without Named Fields to Create Different Types
//
// Rust also supports structs that look similar to tuples, called tuple structs.
// Tuple structs have the added meaning the struct name provides but don’t have
// names associated with their fields; rather, they just have the types of the fields.
// Tuple structs are useful when you want to give the whole tuple a name and
// make the tuple a different type from other tuples, and when
// naming each field as in a regular struct would be verbose or redundant.
//
// To define a tuple struct, start with the struct keyword and the struct name
// followed by the types in the tuple.
pub struct PyRocflError(RocflError);

// Converting from `PyRocflError` to `PyErr`
impl From<PyRocflError> for PyErr {
    fn from(error: PyRocflError) -> Self {
        PyValueError::new_err(error.0.to_string())
    }
}

// Converting from `RocflError` to `PyRocflError`
impl From<RocflError> for PyRocflError {
    fn from(error: RocflError) -> Self {
        Self(error)
    }
}
// Used in python unittest for `RocflError` propagation
fn raise_rocfl_error() -> Result<(), RocflError> {
    Err(RocflError::General("rocfl error".to_string()))
}
// Used in python unittest for `RocflError` propagation
#[pyfunction]
pub fn propagate_rocfl_error() -> Result<(), PyRocflError> {
    raise_rocfl_error()?;
    Ok(())
}

///////////////////////////////////////////////////////////////////////////////
//
// API - Python bindings for rocfl
//
///////////////////////////////////////////////////////////////////////////////

use rocfl::ocfl::LayoutExtensionName;
use rocfl::ocfl::OcflRepo;
use std::path::Path;
use rocfl::ocfl::{SpecVersion, StorageLayout};

#[pyclass]
pub enum PyStorageLayout {
    FlatDirect,
    HashedNTuple,
}

// Initializes a new `OcflRepo` instance backed by the local filesystem.
// The OCFL repository most not already exist.
//
//     pub fn init_fs_repo(
//         storage_root: impl AsRef<Path>,
//         staging: Option<&Path>,
//         version: SpecVersion,
//         layout: Option<StorageLayout>,
//     ) -> Result<Self>
#[pyfunction]
pub fn init_fs_repo(root: &str, layout: &str) -> Result<(), PyRocflError>  {
    let my_root = root;
    let my_staging_root: Option<&Path> = None;

    let my_layout_name = match layout {
        "0002-flat-direct-storage-layout" => LayoutExtensionName::FlatDirectLayout,
        "0004-hashed-n-tuple-storage-layout" => LayoutExtensionName::HashedNTupleLayout,
        _ => return Err(PyRocflError::from(RocflError::General("invalid layout".to_string()))),
    };
    let my_layout: Option<StorageLayout> = Some(StorageLayout::new(my_layout_name, None)?);

    let my_spec_version: SpecVersion = SpecVersion::Ocfl1_1;

    let _repo: OcflRepo = OcflRepo::init_fs_repo(
           my_root,
           my_staging_root,
           my_spec_version,
           my_layout,
    )?;

    Ok(())
}
