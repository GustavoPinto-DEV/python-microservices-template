"""
Chilean RUT (Rol Único Tributario) utilities.

This module centralizes all RUT-related operations using the rut-chile library.
Provides generic functions with robust exception handling for:

- RUT validation
- Formatting in different formats (with/without dots)
- Cleaning and normalization
- Component extraction (number, verification digit)
- RUT construction from separate parts

All services should use these functions instead of custom implementations
or direct use of rut-chile.

Examples:
    >>> validar_rut("12.345.678-5")
    True
    >>> formatear_rut_con_puntos("12345678-5")
    "12.345.678-5"
    >>> separar_rut("12.345.678-5")
    ("12345678", "5")
"""

from typing import Optional, Tuple
from rut_chile import rut_chile
from repositorio_lib.core import logger


# ============================================================================
# VALIDATION
# ============================================================================


def validate_rut(rut: str) -> bool:
    """
    Validate a Chilean RUT using the modulo 11 algorithm.

    Accepts RUTs in any format and validates the verification digit.
    Handles exceptions internally and returns False on errors.

    Args:
        rut: RUT in any format (e.g., "12.345.678-5", "12345678-5", etc.)

    Returns:
        bool: True if RUT is valid, False otherwise

    Examples:
        >>> validate_rut("12.345.678-5")
        True
        >>> validate_rut("12345678-5")
        True
        >>> validate_rut("invalid")
        False
        >>> validate_rut("")
        False
        >>> validate_rut(None)
        False
    """
    if not rut:
        logger.debug("Empty RUT provided for validation")
        return False

    try:
        is_valid = rut_chile.is_valid_rut(str(rut))
        if not is_valid:
            logger.warning(f"Invalid RUT: {rut}")
        else:
            logger.debug(f"Valid RUT: {rut}")
        return is_valid
    except Exception as e:
        logger.error(f"Error validating RUT '{rut}': {e}", exc_info=True)
        return False


# ============================================================================
# CLEANING AND NORMALIZATION
# ============================================================================


def clean_rut(rut: str) -> str:
    """
    Clean and normalize a RUT by removing unnecessary characters.

    Removes dots, spaces and normalizes format to XXXXXXXX-Y.
    Returns empty string if RUT is invalid.

    Args:
        rut: RUT in any format

    Returns:
        str: Clean RUT in format "XXXXXXXX-Y", or empty if invalid

    Examples:
        >>> clean_rut("12.345.678-5")
        "12345678-5"
        >>> clean_rut("  12.345.678-5  ")
        "12345678-5"
        >>> clean_rut("12 345 678-5")
        "12345678-5"
        >>> clean_rut("invalid")
        ""
    """
    if not rut:
        return ""

    try:
        clean_rut_value = rut_chile.clean_rut(str(rut))
        if validate_rut(clean_rut_value):
            logger.debug(f"RUT cleaned: '{rut}' -> '{clean_rut_value}'")
            return clean_rut_value
        logger.warning(f"Could not clean invalid RUT: {rut}")
        return ""
    except Exception as e:
        logger.error(f"Error cleaning RUT '{rut}': {e}", exc_info=True)
        return ""


# ============================================================================
# FORMATTING
# ============================================================================


def format_rut_with_dots(rut: str) -> str:
    """
    Format a RUT to standard format with dots: XX.XXX.XXX-Y.

    Args:
        rut: RUT in any format

    Returns:
        str: RUT formatted with dots, or empty if invalid

    Examples:
        >>> format_rut_with_dots("12345678-5")
        "12.345.678-5"
        >>> format_rut_with_dots("1234567-8")
        "1.234.567-8"
        >>> format_rut_with_dots("invalid")
        ""
    """
    if not rut:
        return ""

    try:
        if not validate_rut(rut):
            return ""

        formatted = rut_chile.format_rut_with_dots(str(rut))
        logger.debug(f"RUT formatted with dots: '{rut}' -> '{formatted}'")
        return formatted
    except Exception as e:
        logger.error(f"Error formatting RUT with dots '{rut}': {e}", exc_info=True)
        return ""


def format_rut_without_dots(rut: str) -> str:
    """
    Format a RUT to format without dots: XXXXXXXX-Y.

    Useful for web forms and database storage.

    Args:
        rut: RUT in any format

    Returns:
        str: RUT without dots in format "XXXXXXXX-Y", or empty if invalid

    Examples:
        >>> format_rut_without_dots("12.345.678-5")
        "12345678-5"
        >>> format_rut_without_dots("12 345 678 - 5")
        "12345678-5"
        >>> format_rut_without_dots("invalid")
        ""
    """
    if not rut:
        return ""

    try:
        if not validate_rut(rut):
            return ""

        formatted = rut_chile.format_rut_without_dots(str(rut))
        logger.debug(f"RUT formatted without dots: '{rut}' -> '{formatted}'")
        return formatted
    except Exception as e:
        logger.error(f"Error formatting RUT without dots '{rut}': {e}", exc_info=True)
        return ""


# ============================================================================
# CONSTRUCTION FROM PARTS
# ============================================================================


def format_complete_rut(base_number: str, verification_digit: str) -> str:
    """
    Build a complete RUT from base number and verification digit.

    Useful when data comes separated (e.g., from APIs or DB).
    Validates that constructed RUT is valid before returning it.

    Args:
        base_number: RUT base number (e.g., "12345678")
        verification_digit: Verification digit (e.g., "5" or "K")

    Returns:
        str: Complete RUT without dots in format "XXXXXXXX-Y", or empty if invalid

    Examples:
        >>> format_complete_rut("12345678", "5")
        "12345678-5"
        >>> format_complete_rut("12345678", "K")
        "12345678-K"
        >>> format_complete_rut("", "5")
        ""
        >>> format_complete_rut("invalid", "X")
        ""
    """
    if not base_number or not verification_digit:
        logger.warning(
            f"Empty RUT parts provided: base='{base_number}', digit='{verification_digit}'"
        )
        return ""

    try:
        concatenated_rut = f"{str(base_number).strip()}-{str(verification_digit).strip()}"

        if concatenated_rut == "-":
            return ""

        if validate_rut(concatenated_rut):
            formatted = format_rut_without_dots(concatenated_rut)
            logger.debug(
                f"RUT built from parts: '{base_number}' + '{verification_digit}' -> '{formatted}'"
            )
            return formatted

        logger.warning(
            f"Invalid RUT constructed from parts: base='{base_number}', digit='{verification_digit}'"
        )
        return ""
    except Exception as e:
        logger.error(
            f"Error building RUT from parts (base='{base_number}', digit='{verification_digit}'): {e}",
            exc_info=True,
        )
        return ""


# ============================================================================
# COMPONENT EXTRACTION
# ============================================================================


def split_rut(rut: str) -> Tuple[str, str]:
    """
    Separate a RUT into base number and verification digit.

    Args:
        rut: RUT in any format

    Returns:
        Tuple[str, str]: Tuple with (base_number, verification_digit)
                        Returns ("", "") if RUT is invalid

    Examples:
        >>> split_rut("12.345.678-5")
        ("12345678", "5")
        >>> split_rut("12345678-K")
        ("12345678", "K")
        >>> split_rut("invalid")
        ("", "")
    """
    if not rut:
        return ("", "")

    try:
        clean_rut_value = clean_rut(rut)
        if not clean_rut_value:
            return ("", "")

        if "-" not in clean_rut_value:
            logger.warning(f"RUT missing dash separator: {rut}")
            return ("", "")

        parts = clean_rut_value.split("-")
        if len(parts) != 2:
            logger.warning(f"RUT has invalid format (expected 2 parts): {rut}")
            return ("", "")

        logger.debug(f"RUT separated: '{rut}' -> ('{parts[0]}', '{parts[1]}')")
        return (parts[0], parts[1])
    except Exception as e:
        logger.error(f"Error separating RUT '{rut}': {e}", exc_info=True)
        return ("", "")


def extract_rut_number(rut: str) -> str:
    """
    Extract only the base number from RUT (without verification digit).

    Args:
        rut: RUT in any format

    Returns:
        str: RUT base number, or empty if invalid

    Examples:
        >>> extract_rut_number("12.345.678-5")
        "12345678"
        >>> extract_rut_number("12345678-K")
        "12345678"
        >>> extract_rut_number("invalid")
        ""
    """
    number, _ = split_rut(rut)
    return number


def extract_verification_digit(rut: str) -> str:
    """
    Extract only the verification digit from RUT.

    Args:
        rut: RUT in any format

    Returns:
        str: Verification digit (0-9 or K), or empty if invalid

    Examples:
        >>> extract_verification_digit("12.345.678-5")
        "5"
        >>> extract_verification_digit("12345678-K")
        "K"
        >>> extract_verification_digit("invalid")
        ""
    """
    _, digit = split_rut(rut)
    return digit


# ============================================================================
# DETAILED VALIDATION
# ============================================================================


def validate_rut_with_details(rut: str) -> dict:
    """
    Validate a RUT and return detailed information.

    Useful for debugging, logging and user error messages.

    Args:
        rut: RUT in any format

    Returns:
        dict: Dictionary with:
            - valid (bool): Whether RUT is valid
            - clean_rut (str): Normalized RUT
            - formatted_rut (str): RUT with dots
            - number (str): Base number
            - digit (str): Verification digit
            - error (str): Error message if not valid

    Examples:
        >>> validate_rut_with_details("12.345.678-5")
        {
            'valid': True,
            'clean_rut': '12345678-5',
            'formatted_rut': '12.345.678-5',
            'number': '12345678',
            'digit': '5',
            'error': ''
        }
    """
    result = {
        "valid": False,
        "clean_rut": "",
        "formatted_rut": "",
        "number": "",
        "digit": "",
        "error": "",
    }

    if not rut:
        result["error"] = "Empty RUT"
        logger.warning("Empty RUT provided for detailed validation")
        return result

    try:
        clean_rut_value = clean_rut(rut)
        if not clean_rut_value:
            result["error"] = (
                "Invalid RUT: incorrect format or wrong verification digit"
            )
            return result

        result["valid"] = True
        result["clean_rut"] = clean_rut_value
        result["formatted_rut"] = format_rut_with_dots(clean_rut_value)

        number, digit = split_rut(clean_rut_value)
        result["number"] = number
        result["digit"] = digit

        logger.debug(f"Detailed RUT validation successful: {result}")
        return result

    except Exception as e:
        result["error"] = f"Error validating RUT: {str(e)}"
        logger.error(f"Error in detailed RUT validation '{rut}': {e}", exc_info=True)
        return result


# ============================================================================
# ADDITIONAL UTILITIES
# ============================================================================


def normalize_rut_list(ruts: list) -> list:
    """
    Normalize a list of RUTs, removing duplicates and invalid ones.

    Args:
        ruts: List of RUTs in any format

    Returns:
        list: List of valid and unique RUTs in format without dots

    Examples:
        >>> normalize_rut_list(["12.345.678-5", "12345678-5", "invalid"])
        ["12345678-5"]
    """
    if not ruts:
        return []

    valid_ruts = set()
    invalid_ruts = []

    for rut in ruts:
        clean_rut_value = clean_rut(rut)
        if clean_rut_value:
            valid_ruts.add(clean_rut_value)
        else:
            invalid_ruts.append(rut)

    if invalid_ruts:
        logger.warning(
            f"Found {len(invalid_ruts)} invalid RUTs in list: {invalid_ruts[:5]}"
        )

    result = sorted(list(valid_ruts))
    logger.debug(
        f"Normalized RUT list: {len(ruts)} input -> {len(result)} valid unique RUTs"
    )
    return result


def is_company_rut(rut: str) -> Optional[bool]:
    """
    Determine if a RUT likely belongs to a company.

    Company RUTs are typically in the 50,000,000+ range.
    This is a heuristic, not an absolute rule.

    Args:
        rut: RUT in any format

    Returns:
        Optional[bool]: True if likely a company, False if likely a person,
                       None if RUT is invalid

    Examples:
        >>> is_company_rut("76.123.456-7")
        True
        >>> is_company_rut("12.345.678-5")
        False
    """
    number = extract_rut_number(rut)
    if not number:
        return None

    try:
        number_int = int(number)
        is_company = number_int >= 50_000_000
        logger.debug(
            f"RUT {rut} classified as: {'company' if is_company else 'person'}"
        )
        return is_company
    except Exception as e:
        logger.error(f"Error determining if RUT is company '{rut}': {e}", exc_info=True)
        return None
