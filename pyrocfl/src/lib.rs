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


use rocfl::ocfl::OcflRepo;
use std::path::Path;
use rocfl::ocfl::{SpecVersion, StorageLayout};
use rocfl::ocfl::RocflError;
use pyo3::exceptions::PyValueError;
use rocfl::ocfl::LayoutExtensionName;

#[pyfunction]
pub fn init_repo(root: &str, layout: &str) -> PyResult<()>  {
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
