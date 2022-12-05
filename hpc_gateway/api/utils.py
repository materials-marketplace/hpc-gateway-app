def expect(input, expected_type, field):
    """To validate the input of the field.
    Only check that the type is expected.
    """
    if isinstance(input, expected_type):
        return input
    raise AssertionError("Invalid input for type", field)
