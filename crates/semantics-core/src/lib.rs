#![forbid(unsafe_code)]
//! Lossless names and explicit presentation policies; no format-specific collation.

use thiserror::Error;
use unicode_normalization::UnicodeNormalization;

#[derive(Clone, Debug, Eq, Hash, PartialEq)]
pub enum RawName {
    Bytes(Vec<u8>),
    Utf16(Vec<u16>),
}

#[derive(Debug, Error)]
pub enum SemanticsError {
    #[error("invalid or overlong filename component")]
    InvalidName,
    #[error("name cannot be represented as Unicode without loss")]
    UnrepresentableName,
    #[error("timestamp is outside the supported range")]
    TimestampRange,
}

impl RawName {
    /// Byte/unit limit is supplied by the format. This is component validation,
    /// not extraction-path validation or a substitute for native collation.
    pub fn validate(&self, max_units: usize) -> Result<(), SemanticsError> {
        let valid = match self {
            Self::Bytes(value) => {
                !value.is_empty()
                    && value.len() <= max_units
                    && !value.iter().any(|unit| *unit == 0 || *unit == b'/')
                    && value != b"."
                    && value != b".."
            }
            Self::Utf16(value) => {
                !value.is_empty()
                    && value.len() <= max_units
                    && !value
                        .iter()
                        .any(|unit| *unit == 0 || *unit == u16::from(b'/'))
                    && value.as_slice() != [u16::from(b'.')]
                    && value.as_slice() != [u16::from(b'.'), u16::from(b'.')]
            }
        };
        if !valid {
            return Err(SemanticsError::InvalidName);
        }
        Ok(())
    }

    /// Lossless conversion only. Non-Unicode bytes and unpaired UTF-16 are kept
    /// in RawName and must be escaped/reversibly mapped by a delivery frontend.
    pub fn unicode(&self) -> Result<String, SemanticsError> {
        match self {
            Self::Bytes(value) => {
                String::from_utf8(value.clone()).map_err(|_| SemanticsError::UnrepresentableName)
            }
            Self::Utf16(value) => {
                String::from_utf16(value).map_err(|_| SemanticsError::UnrepresentableName)
            }
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum Normalization {
    Preserve,
    Nfc,
    Nfd,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum OwnershipPolicy {
    Preserve,
    Synthesize { uid: u32, gid: u32 },
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum AppleDoublePolicy {
    PreserveSidecars,
    InterpretMetadata,
}

#[derive(Clone, Copy, Debug)]
pub struct SemanticsPolicy {
    pub display_normalization: Normalization,
    pub ownership: OwnershipPolicy,
    pub apple_double: AppleDoublePolicy,
    /// A frontend must reject any export that changes these semantics.
    pub reject_lossy_mapping: bool,
}

impl Default for SemanticsPolicy {
    fn default() -> Self {
        Self {
            display_normalization: Normalization::Preserve,
            ownership: OwnershipPolicy::Preserve,
            apple_double: AppleDoublePolicy::PreserveSidecars,
            reject_lossy_mapping: true,
        }
    }
}

impl SemanticsPolicy {
    /// The returned spelling is never a lookup key; detect presentation collisions
    /// before exporting siblings. APFS and exFAT keep their own comparison rules.
    pub fn display_name(&self, name: &RawName) -> Result<String, SemanticsError> {
        let value = name.unicode()?;
        Ok(match self.display_normalization {
            Normalization::Preserve => value,
            Normalization::Nfc => value.nfc().collect(),
            Normalization::Nfd => value.nfd().collect(),
        })
    }
}

/// Canonical signed Unix seconds plus a positive subsecond remainder.
/// On-disk timezone offsets/precision/unknown times remain separate metadata.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct Timestamp {
    seconds: i64,
    nanos: u32,
}

impl Timestamp {
    pub fn new(seconds: i64, nanos: u32) -> Result<Self, SemanticsError> {
        if nanos >= 1_000_000_000 {
            return Err(SemanticsError::TimestampRange);
        }
        Ok(Self { seconds, nanos })
    }
    pub fn from_unix_nanos(value: i128) -> Result<Self, SemanticsError> {
        let seconds = i64::try_from(value.div_euclid(1_000_000_000))
            .map_err(|_| SemanticsError::TimestampRange)?;
        let nanos = u32::try_from(value.rem_euclid(1_000_000_000))
            .map_err(|_| SemanticsError::TimestampRange)?;
        Self::new(seconds, nanos)
    }
    pub fn unix_nanos(self) -> i128 {
        i128::from(self.seconds) * 1_000_000_000 + i128::from(self.nanos)
    }
    pub fn seconds(self) -> i64 {
        self.seconds
    }
    pub fn nanos(self) -> u32 {
        self.nanos
    }
}
