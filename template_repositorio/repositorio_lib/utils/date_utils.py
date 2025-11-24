"""
Date Utils - Date and time handling utilities

Flexible parsing of dates and times from OCR text.
"""

import re
from datetime import date, datetime, time
from typing import Optional
from repositorio_lib.core import logger


def parse_flexible_date(date_str: str) -> Optional[date]:
    """
    Parse a date from multiple possible formats.

    Args:
        date_str: String with date (DD/MM/YYYY, DD/MM/YY, DD-MM-YYYY, etc.)

    Returns:
        date: Date object or None if cannot be parsed

    Examples:
        >>> parse_flexible_date("12/08/2025")
        datetime.date(2025, 8, 12)
        >>> parse_flexible_date("12/8/25")
        datetime.date(2025, 8, 12)
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    patterns = [
        (r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", "%d/%m/%Y"),
        (r"(\d{1,2})[/-](\d{1,2})[/-](\d{2})$", "%d/%m/%y"),
        (r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", "%Y/%m/%d"),
    ]

    for pattern, format_str in patterns:
        match = re.match(pattern, date_str)
        if match:
            try:
                groups = match.groups()
                normalized_date = "/".join(groups)
                parsed_date = datetime.strptime(normalized_date, format_str).date()
                logger.debug(f"Date parsed: '{date_str}' -> {parsed_date}")
                return parsed_date
            except ValueError as e:
                logger.debug(f"Format '{format_str}' not valid for '{date_str}': {e}")
                continue

    logger.warning(f"Could not parse date: '{date_str}'")
    return None


def parse_flexible_time(time_str: str) -> Optional[time]:
    """
    Parse a time from multiple possible formats.

    Args:
        time_str: String with time (HH:MM, HHMM, HH:MM:SS, etc.)

    Returns:
        time: Time object or None if cannot be parsed

    Examples:
        >>> parse_flexible_time("14:30")
        datetime.time(14, 30)
        >>> parse_flexible_time("1430")
        datetime.time(14, 30)
        >>> parse_flexible_time("230")
        datetime.time(2, 30)
    """
    if not time_str:
        return None

    time_str = time_str.strip()
    clean_time = re.sub(r"[^\d:]", "", time_str)

    if ":" in clean_time:
        try:
            parts = clean_time.split(":")
            hh = int(parts[0])
            mm = int(parts[1]) if len(parts) > 1 else 0
            ss = int(parts[2]) if len(parts) > 2 else 0

            if 0 <= hh <= 23 and 0 <= mm <= 59 and 0 <= ss <= 59:
                parsed_time = time(hh, mm, ss)
                logger.debug(f"Time parsed: '{time_str}' -> {parsed_time}")
                return parsed_time
        except ValueError as e:
            logger.debug(f"Error parsing time with ':': '{time_str}': {e}")

    elif clean_time.isdigit():
        if len(clean_time) == 4:
            try:
                hh = int(clean_time[:2])
                mm = int(clean_time[2:])
                if 0 <= hh <= 23 and 0 <= mm <= 59:
                    parsed_time = time(hh, mm)
                    logger.debug(f"Time parsed (HHMM): '{time_str}' -> {parsed_time}")
                    return parsed_time
            except ValueError as e:
                logger.debug(f"Error parsing time HHMM: '{time_str}': {e}")

        elif len(clean_time) == 3:
            try:
                hh = int(clean_time[0])
                mm = int(clean_time[1:])
                if 0 <= hh <= 23 and 0 <= mm <= 59:
                    parsed_time = time(hh, mm)
                    logger.debug(f"Time parsed (HMM): '{time_str}' -> {parsed_time}")
                    return parsed_time
            except ValueError as e:
                logger.debug(f"Error parsing time HMM: '{time_str}': {e}")

    logger.warning(f"Could not parse time: '{time_str}'")
    return None


def calculate_age(birth_date: date) -> Optional[int]:
    """
    Calculate age from a birth date.

    Args:
        birth_date: Birth date

    Returns:
        int: Age in years, or None if date is invalid (future)

    Examples:
        >>> calculate_age(date(1990, 5, 15))
        34  # Depends on current date
    """
    today = date.today()

    if birth_date > today:
        logger.warning(f"Future birth date: {birth_date}")
        return None

    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def validate_date_age_consistency(
    birth_date: date, age: int, tolerance: int = 1
) -> bool:
    """
    Validate that age is consistent with birth date.

    Args:
        birth_date: Birth date
        age: Declared age
        tolerance: Acceptable tolerance in years (default: 1)

    Returns:
        bool: True if consistent within tolerance

    Examples:
        >>> birth_date = date(1990, 5, 15)
        >>> validate_date_age_consistency(birth_date, 34, tolerance=1)
        True
    """
    calculated_age = calculate_age(birth_date)

    if calculated_age is None:
        logger.warning(
            f"Could not validate consistency - invalid date: {birth_date}"
        )
        return False

    is_consistent = abs(calculated_age - age) <= tolerance

    if not is_consistent:
        logger.warning(
            f"Age inconsistency: declared={age}, calculated={calculated_age}, "
            f"date={birth_date}, tolerance={tolerance}"
        )

    return is_consistent


def validate_reasonable_date(
    date_value: date, min_year: int = 1900, max_year: int = None
) -> bool:
    """
    Validate that a date is within a reasonable range.

    Args:
        date_value: Date to validate
        min_year: Minimum acceptable year (default: 1900)
        max_year: Maximum acceptable year (default: current year + 1)

    Returns:
        bool: True if date is reasonable

    Examples:
        >>> validate_reasonable_date(date(2025, 1, 1))
        True
        >>> validate_reasonable_date(date(1850, 1, 1))
        False
    """
    if max_year is None:
        max_year = date.today().year + 1

    is_valid = min_year <= date_value.year <= max_year

    if not is_valid:
        logger.warning(f"Date out of range: {date_value} (range: {min_year}-{max_year})")

    return is_valid
