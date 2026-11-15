use dioryx_transforms::*;

#[test]
fn identity_preserves_blocks_and_rejects_size_mismatch() -> Result<(), TransformError> {
    let mut output = [0; 4];
    IdentityTransform.decode_unit(1, b"data", &mut output)?;
    assert_eq!(&output, b"data");
    assert!(matches!(
        IdentityTransform.decode_unit(1, b"bad", &mut output),
        Err(TransformError::InvalidInput)
    ));
    Ok(())
}

#[test]
fn stream_output_never_exceeds_limit() -> Result<(), TransformError> {
    let data = vec![0x6a; 9000];
    let mut input = data.as_slice();
    let mut output = Vec::new();
    assert!(matches!(
        IdentityTransform.decode(&mut input, &mut output, 8500),
        Err(TransformError::OutputLimit)
    ));
    assert!(output.len() <= 8500);
    output.clear();
    let copied = IdentityTransform.decode(&mut data.as_slice(), &mut output, 9000)?;
    assert_eq!(copied, 9000);
    assert_eq!(output, data);
    Ok(())
}
