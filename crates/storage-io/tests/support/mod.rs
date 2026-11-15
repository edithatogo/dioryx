use std::fs::{File, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};

static NEXT_FILE: AtomicU64 = AtomicU64::new(0);

/// A regular temporary file, not a formatted filesystem fixture.
pub struct TempFile {
    pub path: PathBuf,
}

impl TempFile {
    pub fn new(bytes: &[u8]) -> std::io::Result<Self> {
        for _ in 0..64 {
            let id = NEXT_FILE.fetch_add(1, Ordering::Relaxed);
            let path = std::env::temp_dir()
                .join(format!("universal-fs-contract-{}-{id}", std::process::id()));
            let file = OpenOptions::new().write(true).create_new(true).open(&path);
            match file {
                Ok(mut file) => {
                    let result = Self { path };
                    Self::populate(&mut file, bytes)?;
                    return Ok(result);
                }
                Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(error) => return Err(error),
            }
        }
        Err(std::io::Error::new(
            std::io::ErrorKind::AlreadyExists,
            "temporary file attempts exhausted",
        ))
    }

    fn populate(file: &mut File, bytes: &[u8]) -> std::io::Result<()> {
        file.write_all(bytes)?;
        file.sync_all()
    }
}

impl Drop for TempFile {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.path);
    }
}
