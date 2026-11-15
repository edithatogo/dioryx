#![forbid(unsafe_code)]
//! Bounded transform contracts. Identity is the only admitted implementation.

use std::io::{Read, Write};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum TransformError {
    #[error("transform output limit exceeded")]
    OutputLimit,
    #[error("invalid transform input")]
    InvalidInput,
    #[error("I/O: {0}")]
    Io(#[from] std::io::Error),
}

/// Decodes one complete data unit into an equal-length output. The unit number
/// belongs to the format's cryptographic address space, not a host byte offset.
/// Integrity/authentication is never implied by successful decryption.
pub trait BlockTransform: Send + Sync {
    fn decode_unit(
        &self,
        unit_number: u64,
        input: &[u8],
        output: &mut [u8],
    ) -> Result<(), TransformError>;
}

/// Decodes with a hard output limit and bounded scratch allocation. The caller
/// bounds the input reader and stages output: on error, partial output is invalid.
pub trait StreamTransform: Send + Sync {
    fn decode(
        &self,
        input: &mut dyn Read,
        output: &mut dyn Write,
        max_output: u64,
    ) -> Result<u64, TransformError>;
}

pub struct IdentityTransform;

impl BlockTransform for IdentityTransform {
    fn decode_unit(
        &self,
        _unit_number: u64,
        input: &[u8],
        output: &mut [u8],
    ) -> Result<(), TransformError> {
        if input.len() != output.len() {
            return Err(TransformError::InvalidInput);
        }
        output.copy_from_slice(input);
        Ok(())
    }
}

impl StreamTransform for IdentityTransform {
    fn decode(
        &self,
        input: &mut dyn Read,
        output: &mut dyn Write,
        max_output: u64,
    ) -> Result<u64, TransformError> {
        let mut copied = 0_u64;
        let mut buffer = [0_u8; 8192];
        loop {
            let count = input.read(&mut buffer)?;
            if count == 0 {
                return Ok(copied);
            }
            let next = copied
                .checked_add(count as u64)
                .ok_or(TransformError::OutputLimit)?;
            if next > max_output {
                return Err(TransformError::OutputLimit);
            }
            let bytes = buffer.get(..count).ok_or(TransformError::InvalidInput)?;
            output.write_all(bytes)?;
            copied = next;
        }
    }
}
