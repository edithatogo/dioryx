use semantics_core::*;

#[test]
fn presentation_normalization_does_not_change_identity() -> Result<(), SemanticsError> {
    let composed = RawName::Bytes("é".as_bytes().to_vec());
    let decomposed = RawName::Bytes("e\u{301}".as_bytes().to_vec());
    assert_ne!(composed, decomposed);
    let policy = SemanticsPolicy {
        display_normalization: Normalization::Nfc,
        ..SemanticsPolicy::default()
    };
    assert_eq!(
        policy.display_name(&composed)?,
        policy.display_name(&decomposed)?
    );
    assert_ne!(composed, decomposed);
    let nfd = SemanticsPolicy {
        display_normalization: Normalization::Nfd,
        ..policy
    };
    assert_eq!(nfd.display_name(&composed)?, "e\u{301}");
    Ok(())
}

#[test]
fn non_unicode_names_are_preserved_without_loss() -> Result<(), SemanticsError> {
    for name in [RawName::Bytes(vec![0xff]), RawName::Utf16(vec![0xd800])] {
        name.validate(255)?;
        assert!(matches!(
            name.unicode(),
            Err(SemanticsError::UnrepresentableName)
        ));
    }
    for name in [
        RawName::Bytes(b"../escape".to_vec()),
        RawName::Utf16(vec![0]),
        RawName::Bytes(b"..".to_vec()),
    ] {
        assert!(name.validate(255).is_err());
    }
    Ok(())
}

#[test]
fn timestamps_handle_pre_epoch_values_without_wrapping() -> Result<(), SemanticsError> {
    let before = Timestamp::from_unix_nanos(-1)?;
    assert_eq!(before.seconds(), -1);
    assert_eq!(before.nanos(), 999_999_999);
    assert_eq!(before.unix_nanos(), -1);
    assert!(Timestamp::from_unix_nanos(i128::MAX).is_err());
    assert!(Timestamp::new(0, 1_000_000_000).is_err());
    Ok(())
}
