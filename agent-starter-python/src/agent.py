import json
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    get_job_context,
    inference,
    room_io,
)
from livekit.plugins import noise_cancellation, silero, tavus
from livekit.plugins.turn_detector.multilingual import MultilingualModel

try:
    # Try relative imports first (when running as module)
    from .config import AppConfig
    from .database import DatabaseManager
    from .utils import (
        calculate_costs,
        format_appointment_display,
        format_phone_number,
        parse_date,
        parse_time,
        validate_phone_number,
    )
except ImportError:
    # Fall back to absolute imports (when running directly)
    from config import AppConfig
    from database import DatabaseManager
    from utils import (
        calculate_costs,
        format_appointment_display,
        format_phone_number,
        parse_date,
        parse_time,
        validate_phone_number,
    )

logger = logging.getLogger(__name__)

load_dotenv(".env.local")


class AppointmentAssistant(Agent):
    """AI Voice Agent for booking and managing appointments."""

    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly and professional appointment booking assistant named Alex.

Your responsibilities:
- Help users book, view, modify, and cancel appointments
- Always identify the user by asking for their phone number first before booking
- Confirm all appointment details clearly before finalizing
- Speak naturally and conversationally - this is a voice interaction
- Keep responses concise and to the point
- Be helpful with understanding dates and times (you can understand "tomorrow", "next Monday", etc.)

Important guidelines:
1. When booking:
   - First, identify the user by asking for their phone number
   - Understand their preferred date and time
   - Check availability
   - Confirm ALL details (name, date, time, phone) before finalizing
   - Provide clear confirmation after booking

2. Communication style:
   - You're speaking, not writing - avoid complex punctuation, emojis, or special formatting
   - Be warm and professional
   - Ask clarifying questions if details are unclear
   - Acknowledge when you're checking availability or processing requests

3. Error handling:
   - If a slot is unavailable, offer alternatives
   - If you don't understand something, ask for clarification
   - Be apologetic but helpful when issues arise

Remember: Your goal is to make appointment booking easy and pleasant for users.""",
        )
        self.db = DatabaseManager()
        self.config = AppConfig()
        self.conversation_history = []
        self.current_user = None
        self.session_metrics = {
            "tokens_used": 0,
            "tts_chars": 0,
            "stt_seconds": 0,
        }

    @function_tool()
    async def identify_user(
        self,
        context: RunContext,
        phone_number: str,
    ) -> dict:
        """Identify user by phone number and retrieve their profile.

        Call this function when the user provides their phone number.
        This helps personalize the experience and track their appointments.

        Args:
            phone_number: The user's phone number in any format
        """
        try:
            logger.info(f"Identifying user with phone: {phone_number}")

            # Validate and format phone number
            is_valid, error = validate_phone_number(phone_number)
            if not is_valid:
                return {
                    "success": False,
                    "error": error,
                    "message": f"The phone number seems invalid: {error}. Could you please provide it again?",
                }

            formatted_phone = format_phone_number(phone_number)

            # Check database for existing user
            profile = await self.db.get_user_profile(formatted_phone)

            if profile:
                # Existing user
                self.current_user = {
                    "contact_number": formatted_phone,
                    "name": profile.get("name"),
                    "email": profile.get("email"),
                    "is_new": False,
                }

                return {
                    "success": True,
                    "user": self.current_user,
                    "message": f"Welcome back, {profile.get('name', 'valued customer')}! How can I help you today?",
                }
            else:
                # New user
                self.current_user = {
                    "contact_number": formatted_phone,
                    "name": None,
                    "is_new": True,
                }

                return {
                    "success": True,
                    "user": self.current_user,
                    "message": "I don't have your information yet. May I have your name please?",
                }

        except Exception as e:
            logger.error(f"Error identifying user: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble looking up your information. Could you try again?",
            }

    @function_tool()
    async def fetch_slots(
        self,
        context: RunContext,
        preferred_date: str = "",
    ) -> dict:
        """Fetch available appointment slots.

        Use this to show users what times are available for booking.

        Args:
            preferred_date: Optional preferred date (e.g., "tomorrow", "next Monday", "January 25")
        """
        try:
            logger.info(f"Fetching slots for date: {preferred_date}")

            # Get suggested slots based on preferred date
            slots = self.config.get_slot_suggestions(preferred_date)

            if not slots:
                return {
                    "success": False,
                    "message": "I don't have any available slots for that date. Would you like to try a different day?",
                }

            # Format slots for voice response
            slot_list = []
            for slot in slots[:5]:  # Limit to first 5 for voice
                slot_list.append(
                    {
                        "date": slot["date"],
                        "time": slot["time"],
                        "display": f"{slot['display_date']} at {slot['display_time']}",
                    }
                )

            return {
                "success": True,
                "slots": slot_list,
                "total_available": len(slots),
                "message": f"I have {len(slot_list)} available slots. Here are some options:",
            }

        except Exception as e:
            logger.error(f"Error fetching slots: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble checking availability right now. Please try again.",
            }

    @function_tool()
    async def book_appointment(
        self,
        context: RunContext,
        appointment_date: str,
        appointment_time: str,
        user_name: str,
    ) -> dict:
        """Book an appointment for the user.

        Use this function to create a new appointment after confirming all details with the user.
        IMPORTANT: Make sure the user is identified (phone number collected) before booking.

        Args:
            appointment_date: Date for appointment (e.g., "2026-01-25", "tomorrow", "next Monday")
            appointment_time: Time for appointment (e.g., "2pm", "14:00", "2:30 PM")
            user_name: User's full name
        """
        try:
            logger.info(
                f"Booking appointment for {user_name} on {appointment_date} at {appointment_time}"
            )

            # Check if user is identified
            if not self.current_user or not self.current_user.get("contact_number"):
                return {
                    "success": False,
                    "error": "User not identified",
                    "message": "I need your phone number first before I can book an appointment. Could you provide that?",
                }

            # Parse date and time
            parsed_date = parse_date(appointment_date)
            if not parsed_date:
                return {
                    "success": False,
                    "error": "Invalid date",
                    "message": "I couldn't understand that date. Could you say it differently? For example, tomorrow or January 25th.",
                }

            parsed_time = parse_time(appointment_time)
            if not parsed_time:
                return {
                    "success": False,
                    "error": "Invalid time",
                    "message": "I couldn't understand that time. Could you say it like 2 PM or 2:30 PM?",
                }

            # Validate slot exists in configuration
            date_str = parsed_date.strftime("%Y-%m-%d")
            if not self.config.is_valid_slot(date_str, parsed_time):
                return {
                    "success": False,
                    "error": "Invalid slot",
                    "message": "That time slot isn't available in our system. Would you like to hear available times?",
                }

            # Create appointment
            contact_num = self.current_user["contact_number"]
            if not contact_num:
                raise ValueError("Contact number is required")

            appointment = await self.db.create_appointment(
                contact_number=contact_num,
                user_name=user_name,
                appt_date=parsed_date.date(),
                appt_time=datetime.strptime(parsed_time, "%H:%M").time(),
            )

            # Update current user name if it's a new user
            if self.current_user.get("is_new"):
                self.current_user["name"] = user_name

            # Send notification to frontend via RPC
            await self._send_to_frontend(
                "appointment_booked",
                {
                    "appointment_id": str(appointment["id"]),
                    "user_name": user_name,
                    "date": date_str,
                    "time": parsed_time,
                    "display": format_appointment_display(appointment),
                },
            )

            return {
                "success": True,
                "appointment": appointment,
                "message": f"Perfect! I've booked your appointment for {format_appointment_display(appointment)}. You'll receive a confirmation shortly.",
            }

        except ValueError as ve:
            # This catches slot unavailability from database
            logger.warning(f"Slot not available: {ve}")
            return {
                "success": False,
                "error": str(ve),
                "message": f"Sorry, that time slot is already booked. Would you like to choose a different time?",
            }
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I had trouble booking that appointment. Could you try again?",
            }

    @function_tool()
    async def retrieve_appointments(
        self,
        context: RunContext,
    ) -> dict:
        """Retrieve all active appointments for the current user.

        Use this when the user wants to see their upcoming appointments.
        """
        try:
            logger.info("Retrieving appointments for current user")

            # Check if user is identified
            if not self.current_user or not self.current_user.get("contact_number"):
                return {
                    "success": False,
                    "error": "User not identified",
                    "message": "I need your phone number first to look up your appointments. What's your phone number?",
                }

            # Get appointments from database
            appointments = await self.db.get_user_appointments(
                self.current_user["contact_number"]
            )

            if not appointments:
                return {
                    "success": True,
                    "appointments": [],
                    "message": "You don't have any upcoming appointments. Would you like to book one?",
                }

            # Format appointments for voice response
            appt_list = []
            for appt in appointments:
                appt_list.append(
                    {
                        "id": str(appt["id"]),
                        "date": appt["appointment_date"],
                        "time": appt["appointment_time"],
                        "display": format_appointment_display(appt),
                    }
                )

            return {
                "success": True,
                "appointments": appt_list,
                "message": f"You have {len(appt_list)} upcoming appointment{'s' if len(appt_list) != 1 else ''}.",
            }

        except Exception as e:
            logger.error(f"Error retrieving appointments: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble retrieving your appointments. Please try again.",
            }

    @function_tool()
    async def cancel_appointment(
        self,
        context: RunContext,
        appointment_identifier: str,
    ) -> dict:
        """Cancel a specific appointment.

        Use this when the user wants to cancel an appointment.
        The appointment can be identified by its ID, date, or time.

        Args:
            appointment_identifier: The appointment ID, date, or description to cancel
        """
        try:
            logger.info(f"Cancelling appointment: {appointment_identifier}")

            # Check if user is identified
            if not self.current_user or not self.current_user.get("contact_number"):
                return {
                    "success": False,
                    "error": "User not identified",
                    "message": "I need your phone number first. What's your phone number?",
                }

            # Get user's appointments
            appointments = await self.db.get_user_appointments(
                self.current_user["contact_number"]
            )

            if not appointments:
                return {
                    "success": False,
                    "message": "You don't have any appointments to cancel.",
                }

            # Try to find matching appointment
            target_appointment = None

            # First, try exact ID match
            for appt in appointments:
                if str(appt["id"]) == appointment_identifier:
                    target_appointment = appt
                    break

            # If not found, try date matching
            if not target_appointment:
                parsed_date = parse_date(appointment_identifier)
                if parsed_date:
                    date_str = parsed_date.strftime("%Y-%m-%d")
                    for appt in appointments:
                        if appt["appointment_date"] == date_str:
                            target_appointment = appt
                            break

            # If still not found and only one appointment, assume it's that one
            if not target_appointment and len(appointments) == 1:
                target_appointment = appointments[0]

            if not target_appointment:
                return {
                    "success": False,
                    "message": "I couldn't find that appointment. Could you specify which one you'd like to cancel?",
                }

            # Cancel the appointment
            success = await self.db.cancel_appointment(str(target_appointment["id"]))

            if success:
                # Notify frontend
                await self._send_to_frontend(
                    "appointment_cancelled",
                    {
                        "appointment_id": str(target_appointment["id"]),
                        "date": target_appointment["appointment_date"],
                        "time": target_appointment["appointment_time"],
                    },
                )

                return {
                    "success": True,
                    "message": f"I've cancelled your appointment for {format_appointment_display(target_appointment)}.",
                }
            else:
                return {
                    "success": False,
                    "message": "I had trouble cancelling that appointment. Could you try again?",
                }

        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble cancelling that appointment. Please try again.",
            }

    @function_tool()
    async def modify_appointment(
        self,
        context: RunContext,
        appointment_identifier: str,
        new_date: str,
        new_time: str,
    ) -> dict:
        """Modify an existing appointment's date and/or time.

        Use this when the user wants to reschedule an appointment.

        Args:
            appointment_identifier: The appointment ID, date, or description to modify
            new_date: New date for the appointment
            new_time: New time for the appointment
        """
        try:
            logger.info(
                f"Modifying appointment {appointment_identifier} to {new_date} at {new_time}"
            )

            # Check if user is identified
            if not self.current_user or not self.current_user.get("contact_number"):
                return {
                    "success": False,
                    "error": "User not identified",
                    "message": "I need your phone number first. What's your phone number?",
                }

            # Get user's appointments
            appointments = await self.db.get_user_appointments(
                self.current_user["contact_number"]
            )

            if not appointments:
                return {
                    "success": False,
                    "message": "You don't have any appointments to modify.",
                }

            # Find target appointment (similar logic to cancel)
            target_appointment = None
            for appt in appointments:
                if str(appt["id"]) == appointment_identifier:
                    target_appointment = appt
                    break

            if not target_appointment and len(appointments) == 1:
                target_appointment = appointments[0]

            if not target_appointment:
                return {
                    "success": False,
                    "message": "I couldn't find that appointment. Could you specify which one you'd like to modify?",
                }

            # Parse new date and time
            parsed_date = parse_date(new_date)
            if not parsed_date:
                return {
                    "success": False,
                    "error": "Invalid date",
                    "message": "I couldn't understand that date. Could you say it differently?",
                }

            parsed_time = parse_time(new_time)
            if not parsed_time:
                return {
                    "success": False,
                    "error": "Invalid time",
                    "message": "I couldn't understand that time. Could you say it like 2 PM?",
                }

            # Validate new slot
            date_str = parsed_date.strftime("%Y-%m-%d")
            if not self.config.is_valid_slot(date_str, parsed_time):
                return {
                    "success": False,
                    "error": "Invalid slot",
                    "message": "That time slot isn't available. Would you like to hear available times?",
                }

            # Modify appointment
            updated = await self.db.modify_appointment(
                str(target_appointment["id"]),
                parsed_date.date(),
                datetime.strptime(parsed_time, "%H:%M").time(),
            )

            # Notify frontend
            await self._send_to_frontend(
                "appointment_modified",
                {
                    "appointment_id": str(updated["id"]),
                    "old_date": target_appointment["appointment_date"],
                    "old_time": target_appointment["appointment_time"],
                    "new_date": date_str,
                    "new_time": parsed_time,
                    "display": format_appointment_display(updated),
                },
            )

            return {
                "success": True,
                "appointment": updated,
                "message": f"Great! I've rescheduled your appointment to {format_appointment_display(updated)}.",
            }

        except ValueError as ve:
            logger.warning(f"New slot not available: {ve}")
            return {
                "success": False,
                "error": str(ve),
                "message": "Sorry, that new time slot is already booked. Would you like to choose a different time?",
            }
        except Exception as e:
            logger.error(f"Error modifying appointment: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "I had trouble modifying that appointment. Could you try again?",
            }

    @function_tool()
    async def end_conversation(
        self,
        context: RunContext,
    ) -> None:
        """End the conversation and generate a summary.

        Call this when the user indicates they're done or wants to end the call.
        This will create a summary of the conversation and display it to the user.
        """
        try:
            logger.info("Ending conversation and generating summary")

            # Generate conversation summary using LLM
            user_context = "was not identified"
            if self.current_user:
                user_id = (
                    self.current_user.get("name")
                    or self.current_user.get("contact_number")
                    or "unknown"
                )
                user_context = f"identified as {user_id}"

            summary_prompt = f"""Based on our conversation, create a brief summary (2-3 sentences) covering:
- What the user wanted to accomplish
- Any appointments booked, modified, or cancelled
- Any preferences or notes mentioned

Conversation context: User {user_context}
"""

            # Get appointments discussed in this session
            appointments_discussed = []
            if self.current_user and self.current_user.get("contact_number"):
                recent_appointments = await self.db.get_user_appointments(
                    self.current_user["contact_number"]
                )
                appointments_discussed = [
                    {
                        "date": appt["appointment_date"],
                        "time": appt["appointment_time"],
                        "status": appt["status"],
                    }
                    for appt in recent_appointments[:3]  # Last 3 appointments
                ]

            # Simple summary (in production, you'd use the LLM to generate this)
            summary = "Thank you for using our appointment booking service. "
            if self.current_user:
                user_name_display = self.current_user.get("name") or "you"
                summary += f"We helped {user_name_display} "
                if appointments_discussed:
                    summary += f"manage {len(appointments_discussed)} appointment(s). "
            summary += "Have a great day!"

            # Calculate costs (bonus feature)
            costs = calculate_costs(
                tokens_used=self.session_metrics.get("tokens_used", 0),
                tts_chars=self.session_metrics.get("tts_chars", 0),
                stt_seconds=self.session_metrics.get("stt_seconds", 0),
            )

            # Save summary to database
            session_id = get_job_context().room.name
            await self.db.save_conversation_summary(
                session_id=session_id,
                summary=summary,
                contact_number=(
                    self.current_user.get("contact_number")
                    if self.current_user
                    else None
                ),
                appointments=appointments_discussed,
                cost_breakdown=costs,
            )

            # Send summary to frontend
            await self._send_to_frontend(
                "conversation_summary",
                {
                    "summary": summary,
                    "appointments": appointments_discussed,
                    "costs": costs,
                    "user": self.current_user,
                },
            )

            logger.info("Conversation ended successfully")

        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            # Don't raise - try to end gracefully anyway

    async def _send_to_frontend(self, event_type: str, data: dict):
        """
        Send data to frontend via RPC.

        Args:
            event_type: Type of event (e.g., "appointment_booked")
            data: Data payload to send
        """
        try:
            room = get_job_context().room
            # Get first remote participant
            remote_participants = list(room.remote_participants.values())
            if not remote_participants:
                logger.warning("No remote participants to send RPC to")
                return

            participant = remote_participants[0]

            await room.local_participant.perform_rpc(
                destination_identity=participant.identity,
                method=event_type,
                payload=json.dumps(data),
                response_timeout=5.0,
            )

            logger.info(f"Sent {event_type} event to frontend")

        except Exception as e:
            logger.error(f"Error sending to frontend: {e}")
            # Don't raise - this shouldn't block the main flow


server = AgentServer()


def prewarm(proc: JobProcess):
    """Prewarm resources before agent starts."""
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session()
async def my_agent(ctx: JobContext):
    """Main agent entry point."""
    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    logger.info(f"Starting appointment assistant agent for room {ctx.room.name}")

    # Set up voice AI pipeline
    session = AgentSession(
        # Use Deepgram for STT
        stt=inference.STT(model="deepgram/nova-2", language="en"),
        # Use OpenAI for LLM
        llm=inference.LLM(model="openai/gpt-4o-mini"),
        # Use Cartesia for TTS
        tts=inference.TTS(
            model="cartesia/sonic-3", voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc"
        ),
        # VAD and turn detection
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # Allow preemptive generation
        preemptive_generation=True,
    )

    # Add Tavus avatar if configured
    tavus_replica_id = os.getenv("TAVUS_REPLICA_ID")
    tavus_persona_id = os.getenv("TAVUS_PERSONA_ID")

    if tavus_replica_id and tavus_persona_id:
        try:
            logger.info("Initializing Tavus avatar")
            avatar = tavus.AvatarSession(
                replica_id=tavus_replica_id,
                persona_id=tavus_persona_id,
            )
            await avatar.start(session, room=ctx.room)
            logger.info("Tavus avatar started successfully")
        except Exception as e:
            logger.error(f"Failed to start Tavus avatar: {e}")
            # Continue without avatar
    else:
        logger.warning("Tavus credentials not configured - running without avatar")

    # Start the session
    await session.start(
        agent=AppointmentAssistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony()
                if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                else noise_cancellation.BVC(),
            ),
        ),
    )

    # Join the room
    await ctx.connect()

    logger.info("Agent connected and ready")


if __name__ == "__main__":
    cli.run_app(server)
