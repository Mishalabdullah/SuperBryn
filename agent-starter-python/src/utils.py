"""Utility functions for date parsing, phone formatting, and cost calculation."""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from dateutil import parser as date_parser

logger = logging.getLogger(__name__)


def format_phone_number(phone: str) -> str:
    """
    Standardize phone number format by removing all non-digit characters.

    Args:
        phone: Phone number in any format

    Returns:
        Phone number with only digits
    """
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)
    logger.debug(f"Formatted phone number: {phone} -> {digits}")
    return digits


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse various date formats to datetime object.
    Handles natural language like "tomorrow", "next monday", specific dates, etc.

    Args:
        date_str: Date string in various formats

    Returns:
        datetime object or None if parsing fails
    """
    try:
        date_str_lower = date_str.lower().strip()

        # Handle common natural language dates
        if date_str_lower in ["today", "now"]:
            return datetime.now()
        elif date_str_lower == "tomorrow":
            return datetime.now() + timedelta(days=1)
        elif date_str_lower == "day after tomorrow":
            return datetime.now() + timedelta(days=2)
        elif date_str_lower.startswith("next monday"):
            return get_next_weekday(0)  # Monday
        elif date_str_lower.startswith("next tuesday"):
            return get_next_weekday(1)  # Tuesday
        elif date_str_lower.startswith("next wednesday"):
            return get_next_weekday(2)  # Wednesday
        elif date_str_lower.startswith("next thursday"):
            return get_next_weekday(3)  # Thursday
        elif date_str_lower.startswith("next friday"):
            return get_next_weekday(4)  # Friday
        elif date_str_lower.startswith("next saturday"):
            return get_next_weekday(5)  # Saturday
        elif date_str_lower.startswith("next sunday"):
            return get_next_weekday(6)  # Sunday

        # Try to parse with dateutil parser (handles many formats)
        parsed_date = date_parser.parse(date_str, fuzzy=True)
        logger.debug(f"Parsed date: {date_str} -> {parsed_date}")
        return parsed_date

    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {e}")
        return None


def get_next_weekday(weekday: int) -> datetime:
    """
    Get the next occurrence of a specific weekday.

    Args:
        weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday

    Returns:
        datetime of next occurrence
    """
    today = datetime.now()
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def parse_time(time_str: str) -> Optional[str]:
    """
    Parse time to HH:MM format (24-hour).
    Handles formats like "2pm", "14:00", "two thirty", "2:30 PM", etc.

    Args:
        time_str: Time string in various formats

    Returns:
        Time in HH:MM format or None if parsing fails
    """
    try:
        time_str_lower = time_str.lower().strip()

        # Handle common natural language times
        time_mappings = {
            "noon": "12:00",
            "midnight": "00:00",
            "morning": "09:00",
            "afternoon": "14:00",
            "evening": "18:00",
        }

        if time_str_lower in time_mappings:
            return time_mappings[time_str_lower]

        # Remove common words
        time_str_clean = (
            time_str_lower.replace("o'clock", "")
            .replace("at", "")
            .replace("around", "")
            .strip()
        )

        # Try to parse with dateutil
        try:
            # Add a dummy date to help with parsing
            parsed = date_parser.parse(f"2024-01-01 {time_str_clean}", fuzzy=True)
            result = parsed.strftime("%H:%M")
            logger.debug(f"Parsed time: {time_str} -> {result}")
            return result
        except Exception:
            pass

        # Try regex patterns for common formats
        # Pattern: 2pm, 2 pm, 14:00, 2:30pm, etc.
        patterns = [
            r"(\d{1,2}):(\d{2})\s*(am|pm)?",  # 2:30pm, 14:30
            r"(\d{1,2})\s*(am|pm)",  # 2pm, 2 pm
            r"(\d{1,2})(?::(\d{2}))?",  # 14, 14:30
        ]

        for pattern in patterns:
            match = re.search(pattern, time_str_clean)
            if match:
                hour = int(match.group(1))
                minute = (
                    int(match.group(2))
                    if len(match.groups()) > 1 and match.group(2)
                    else 0
                )
                meridiem = match.group(3) if len(match.groups()) > 2 else None

                # Convert to 24-hour format if PM
                if meridiem:
                    if meridiem == "pm" and hour < 12:
                        hour += 12
                    elif meridiem == "am" and hour == 12:
                        hour = 0

                result = f"{hour:02d}:{minute:02d}"
                logger.debug(f"Parsed time: {time_str} -> {result}")
                return result

        logger.error(f"Could not parse time: {time_str}")
        return None

    except Exception as e:
        logger.error(f"Error parsing time '{time_str}': {e}")
        return None


def calculate_costs(
    tokens_used: int = 0, tts_chars: int = 0, stt_seconds: int = 0
) -> Dict[str, float]:
    """
    Calculate API costs breakdown based on usage.

    Pricing (as of 2024):
    - OpenAI GPT-4o-mini: ~$0.15/1M input tokens, ~$0.60/1M output tokens (avg $0.30/1M)
    - Cartesia TTS: ~$0.015/1K characters
    - Deepgram STT: ~$0.0043/minute

    Args:
        tokens_used: Total tokens used by LLM
        tts_chars: Total characters synthesized
        stt_seconds: Total seconds of speech transcribed

    Returns:
        Dictionary with cost breakdown
    """
    try:
        costs = {
            "llm_cost": round(tokens_used * 0.30 / 1_000_000, 6),  # OpenAI pricing
            "tts_cost": round(tts_chars * 0.015 / 1000, 6),  # Cartesia pricing
            "stt_cost": round(stt_seconds * 0.0043 / 60, 6),  # Deepgram pricing
            "total_cost": 0.0,
        }

        costs["total_cost"] = round(
            costs["llm_cost"] + costs["tts_cost"] + costs["stt_cost"], 6
        )

        logger.debug(f"Cost calculation: {costs}")
        return costs

    except Exception as e:
        logger.error(f"Error calculating costs: {e}")
        return {
            "llm_cost": 0.0,
            "tts_cost": 0.0,
            "stt_cost": 0.0,
            "total_cost": 0.0,
        }


def format_appointment_display(appointment: Dict) -> str:
    """
    Format appointment data for display to user.

    Args:
        appointment: Appointment dictionary

    Returns:
        Formatted string for voice output
    """
    try:
        # Parse date and time
        appt_date = datetime.strptime(
            appointment["appointment_date"], "%Y-%m-%d"
        ).strftime("%A, %B %d, %Y")
        appt_time = datetime.strptime(
            appointment["appointment_time"], "%H:%M:%S"
        ).strftime("%I:%M %p")

        return f"{appt_date} at {appt_time}"

    except Exception as e:
        logger.error(f"Error formatting appointment: {e}")
        return f"{appointment.get('appointment_date', 'Unknown date')} at {appointment.get('appointment_time', 'Unknown time')}"


def validate_phone_number(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format.

    Args:
        phone: Phone number string

    Returns:
        Tuple of (is_valid, error_message)
    """
    formatted = format_phone_number(phone)

    if len(formatted) < 7:
        return False, "Phone number too short"

    if len(formatted) > 15:
        return False, "Phone number too long"

    if not formatted.isdigit():
        return False, "Phone number contains invalid characters"

    return True, None
