"""Database operations for Supabase integration."""

import logging
import os
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages all database operations with Supabase."""

    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )

        self.supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Database manager initialized successfully")

    # ==================== USER PROFILE METHODS ====================

    async def get_user_profile(self, contact_number: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user profile by phone number.

        Args:
            contact_number: User's phone number

        Returns:
            User profile dict or None if not found
        """
        try:
            response = (
                self.supabase.table("user_profiles")
                .select("*")
                .eq("contact_number", contact_number)
                .execute()
            )

            if response.data and len(response.data) > 0:
                logger.info(f"User profile found for {contact_number}")
                return response.data[0]
            else:
                logger.info(f"No user profile found for {contact_number}")
                return None

        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return None

    async def create_user_profile(
        self, contact_number: str, name: str, email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new user profile.

        Args:
            contact_number: User's phone number
            name: User's full name
            email: User's email (optional)

        Returns:
            Created user profile dict
        """
        try:
            data = {"contact_number": contact_number, "name": name}
            if email:
                data["email"] = email

            response = self.supabase.table("user_profiles").insert(data).execute()

            logger.info(f"User profile created for {contact_number}")
            return response.data[0] if response.data else data

        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise

    async def update_user_profile(
        self, contact_number: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing user profile.

        Args:
            contact_number: User's phone number
            updates: Dictionary of fields to update

        Returns:
            Updated user profile dict
        """
        try:
            response = (
                self.supabase.table("user_profiles")
                .update(updates)
                .eq("contact_number", contact_number)
                .execute()
            )

            logger.info(f"User profile updated for {contact_number}")
            return response.data[0] if response.data else {}

        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise

    # ==================== APPOINTMENT METHODS ====================

    async def check_slot_available(
        self, appt_date: date, appt_time: time
    ) -> tuple[bool, Optional[str]]:
        """
        Check if appointment slot is available.

        Args:
            appt_date: Appointment date
            appt_time: Appointment time

        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            # Check for active appointments at this slot
            response = (
                self.supabase.table("appointments")
                .select("id, user_name")
                .eq("appointment_date", str(appt_date))
                .eq("appointment_time", str(appt_time))
                .eq("status", "active")
                .execute()
            )

            if response.data and len(response.data) > 0:
                logger.info(f"Slot {appt_date} {appt_time} is already booked")
                return False, "This time slot is already booked"
            else:
                logger.info(f"Slot {appt_date} {appt_time} is available")
                return True, None

        except Exception as e:
            logger.error(f"Error checking slot availability: {e}")
            return False, f"Error checking availability: {str(e)}"

    async def create_appointment(
        self,
        contact_number: str,
        user_name: str,
        appt_date: date,
        appt_time: time,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create new appointment.

        Args:
            contact_number: User's phone number
            user_name: User's full name
            appt_date: Appointment date
            appt_time: Appointment time
            notes: Optional appointment notes

        Returns:
            Created appointment dict
        """
        try:
            # First check if slot is available
            is_available, error = await self.check_slot_available(appt_date, appt_time)
            if not is_available:
                raise ValueError(error or "Slot not available")

            # Ensure user profile exists
            profile = await self.get_user_profile(contact_number)
            if not profile:
                await self.create_user_profile(contact_number, user_name)

            # Create appointment
            data = {
                "contact_number": contact_number,
                "user_name": user_name,
                "appointment_date": str(appt_date),
                "appointment_time": str(appt_time),
                "status": "active",
            }
            if notes:
                data["notes"] = notes

            response = self.supabase.table("appointments").insert(data).execute()

            logger.info(
                f"Appointment created for {user_name} on {appt_date} at {appt_time}"
            )
            return response.data[0] if response.data else data

        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            raise

    async def get_user_appointments(
        self, contact_number: str, include_cancelled: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve appointments for a user.

        Args:
            contact_number: User's phone number
            include_cancelled: Whether to include cancelled appointments

        Returns:
            List of appointment dicts
        """
        try:
            query = (
                self.supabase.table("appointments")
                .select("*")
                .eq("contact_number", contact_number)
                .order("appointment_date", desc=False)
                .order("appointment_time", desc=False)
            )

            if not include_cancelled:
                query = query.eq("status", "active")

            response = query.execute()

            appointments = response.data if response.data else []
            logger.info(
                f"Retrieved {len(appointments)} appointments for {contact_number}"
            )
            return appointments

        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            return []

    async def get_appointment_by_id(
        self, appointment_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get appointment by ID.

        Args:
            appointment_id: UUID of the appointment

        Returns:
            Appointment dict or None
        """
        try:
            response = (
                self.supabase.table("appointments")
                .select("*")
                .eq("id", appointment_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None

        except Exception as e:
            logger.error(f"Error fetching appointment: {e}")
            return None

    async def cancel_appointment(self, appointment_id: str) -> bool:
        """
        Cancel an appointment.

        Args:
            appointment_id: UUID of the appointment to cancel

        Returns:
            True if successful, False otherwise
        """
        try:
            response = (
                self.supabase.table("appointments")
                .update({"status": "cancelled"})
                .eq("id", appointment_id)
                .execute()
            )

            if response.data:
                logger.info(f"Appointment {appointment_id} cancelled")
                return True
            return False

        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return False

    async def modify_appointment(
        self, appointment_id: str, new_date: date, new_time: time
    ) -> Dict[str, Any]:
        """
        Modify appointment date/time.

        Args:
            appointment_id: UUID of the appointment
            new_date: New appointment date
            new_time: New appointment time

        Returns:
            Updated appointment dict
        """
        try:
            # Check if new slot is available
            is_available, error = await self.check_slot_available(new_date, new_time)
            if not is_available:
                raise ValueError(error or "New slot not available")

            # Update appointment
            response = (
                self.supabase.table("appointments")
                .update(
                    {
                        "appointment_date": str(new_date),
                        "appointment_time": str(new_time),
                        "status": "active",
                    }
                )
                .eq("id", appointment_id)
                .execute()
            )

            logger.info(
                f"Appointment {appointment_id} modified to {new_date} at {new_time}"
            )
            return response.data[0] if response.data else {}

        except Exception as e:
            logger.error(f"Error modifying appointment: {e}")
            raise

    # ==================== CONVERSATION SUMMARY METHODS ====================

    async def save_conversation_summary(
        self,
        session_id: str,
        summary: str,
        contact_number: Optional[str] = None,
        appointments: Optional[List[Dict[str, Any]]] = None,
        user_preferences: Optional[str] = None,
        cost_breakdown: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Save conversation summary.

        Args:
            session_id: LiveKit session ID
            summary: Conversation summary text
            contact_number: User's phone number (if identified)
            appointments: List of appointments mentioned
            user_preferences: Any preferences mentioned
            cost_breakdown: Optional cost breakdown

        Returns:
            Created summary dict
        """
        try:
            data = {
                "session_id": session_id,
                "summary": summary,
                "contact_number": contact_number,
                "appointments_mentioned": appointments or [],
                "user_preferences": user_preferences,
                "cost_breakdown": cost_breakdown or {},
            }

            response = (
                self.supabase.table("conversation_summaries").insert(data).execute()
            )

            logger.info(f"Conversation summary saved for session {session_id}")
            return response.data[0] if response.data else data

        except Exception as e:
            logger.error(f"Error saving conversation summary: {e}")
            raise

    async def get_conversation_summary(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation summary by session ID.

        Args:
            session_id: LiveKit session ID

        Returns:
            Summary dict or None
        """
        try:
            response = (
                self.supabase.table("conversation_summaries")
                .select("*")
                .eq("session_id", session_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None

        except Exception as e:
            logger.error(f"Error fetching conversation summary: {e}")
            return None
