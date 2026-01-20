"""Configuration management for appointment slots and application settings."""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class AppConfig:
    """Manages application configuration including appointment slots."""

    def __init__(self):
        """Initialize configuration."""
        self.config_file = Path(__file__).parent / "slots_config.json"
        self.load_slots_config()
        logger.info("App configuration loaded successfully")

    def load_slots_config(self):
        """Load appointment slots configuration from JSON file or use defaults."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.available_times = config.get(
                        "available_times",
                        [
                            "09:00",
                            "09:30",
                            "10:00",
                            "10:30",
                            "11:00",
                            "11:30",
                            "14:00",
                            "14:30",
                            "15:00",
                            "15:30",
                            "16:00",
                            "16:30",
                        ],
                    )
                    self.days_ahead = config.get("days_ahead", 14)
                    self.excluded_weekdays = config.get("excluded_weekdays", [5, 6])
                    self.duration_minutes = config.get("duration_minutes", 30)
                    self.business_hours = config.get(
                        "business_hours", {"start": "09:00", "end": "17:00"}
                    )
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                # Use defaults
                self.available_times = [
                    "09:00",
                    "09:30",
                    "10:00",
                    "10:30",
                    "11:00",
                    "11:30",
                    "14:00",
                    "14:30",
                    "15:00",
                    "15:30",
                    "16:00",
                    "16:30",
                ]
                self.days_ahead = 14
                self.excluded_weekdays = [5, 6]  # Saturday, Sunday
                self.duration_minutes = 30
                self.business_hours = {"start": "09:00", "end": "17:00"}
                logger.warning(
                    f"Config file not found at {self.config_file}, using defaults"
                )

        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            # Use defaults on error
            self.available_times = [
                "09:00",
                "09:30",
                "10:00",
                "10:30",
                "11:00",
                "11:30",
                "14:00",
                "14:30",
                "15:00",
                "15:30",
                "16:00",
                "16:30",
            ]
            self.days_ahead = 14
            self.excluded_weekdays = [5, 6]
            self.duration_minutes = 30
            self.business_hours = {"start": "09:00", "end": "17:00"}

    def get_available_slots(
        self, from_date: datetime = None, days: int = None
    ) -> List[Dict[str, str]]:
        """
        Generate available slots for next N days.

        Args:
            from_date: Starting date (defaults to today)
            days: Number of days to generate slots for (defaults to self.days_ahead)

        Returns:
            List of slot dictionaries with 'date', 'time', and 'datetime' fields
        """
        if from_date is None:
            from_date = datetime.now()

        if days is None:
            days = self.days_ahead

        slots = []
        current_date = from_date.date()

        for day_offset in range(days):
            check_date = current_date + timedelta(days=day_offset)

            # Skip excluded weekdays (0=Monday, 6=Sunday)
            if check_date.weekday() in self.excluded_weekdays:
                continue

            # Add all available time slots for this day
            for time_str in self.available_times:
                slots.append(
                    {
                        "date": check_date.strftime("%Y-%m-%d"),
                        "time": time_str,
                        "datetime": f"{check_date.strftime('%Y-%m-%d')} {time_str}",
                        "display_date": check_date.strftime("%A, %B %d, %Y"),
                        "display_time": self._format_time_12hr(time_str),
                    }
                )

        logger.info(f"Generated {len(slots)} available slots")
        return slots

    def is_valid_slot(self, slot_date: str, slot_time: str) -> bool:
        """
        Validate if a slot exists in configuration.

        Args:
            slot_date: Date string (YYYY-MM-DD)
            slot_time: Time string (HH:MM)

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if time is in available times
            if slot_time not in self.available_times:
                return False

            # Parse date and check if it's in the future
            date_obj = datetime.strptime(slot_date, "%Y-%m-%d").date()
            today = datetime.now().date()

            if date_obj < today:
                return False

            # Check if date is within allowed range
            max_date = today + timedelta(days=self.days_ahead)
            if date_obj > max_date:
                return False

            # Check if weekday is allowed
            if date_obj.weekday() in self.excluded_weekdays:
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating slot: {e}")
            return False

    def _format_time_12hr(self, time_24hr: str) -> str:
        """
        Convert 24-hour time to 12-hour format with AM/PM.

        Args:
            time_24hr: Time string in HH:MM format

        Returns:
            Time string in 12-hour format (e.g., "2:30 PM")
        """
        try:
            time_obj = datetime.strptime(time_24hr, "%H:%M")
            return time_obj.strftime("%I:%M %p").lstrip("0")
        except Exception:
            return time_24hr

    def get_slot_suggestions(self, preferred_date: str = None) -> List[Dict[str, str]]:
        """
        Get suggested slots, optionally filtered by preferred date.

        Args:
            preferred_date: Optional date to filter by (YYYY-MM-DD or natural language)

        Returns:
            List of suggested slot dictionaries
        """
        all_slots = self.get_available_slots()

        if preferred_date:
            # Try to parse preferred date
            try:
                if preferred_date.lower() == "today":
                    target_date = datetime.now().date()
                elif preferred_date.lower() == "tomorrow":
                    target_date = (datetime.now() + timedelta(days=1)).date()
                else:
                    target_date = datetime.strptime(preferred_date, "%Y-%m-%d").date()

                # Filter slots by date
                filtered_slots = [
                    slot for slot in all_slots if slot["date"] == str(target_date)
                ]
                return filtered_slots if filtered_slots else all_slots[:10]
            except Exception:
                # Return first 10 slots if parsing fails
                return all_slots[:10]

        # Return next 10 available slots
        return all_slots[:10]
