import { LocalParticipant, RpcInvocationData } from 'livekit-client';
import type { Appointment, ConversationSummary } from './types';

interface RpcHandlerCallbacks {
  onAppointmentBooked?: (appointment: Appointment) => void;
  onAppointmentCancelled?: (data: { appointment_id: string; date: string; time: string }) => void;
  onAppointmentModified?: (data: {
    appointment_id: string;
    old_date: string;
    old_time: string;
    new_date: string;
    new_time: string;
    display: string;
  }) => void;
  onConversationSummary?: (summary: ConversationSummary) => void;
  onToolCallUpdate?: (data: any) => void;
}

export function registerRpcHandlers(
  localParticipant: LocalParticipant,
  callbacks: RpcHandlerCallbacks
) {
  console.log('Registering RPC handlers...');

  // Handle appointment booked
  localParticipant.registerRpcMethod('appointment_booked', async (data: RpcInvocationData) => {
    try {
      const payload = JSON.parse(data.payload);
      console.log('Appointment booked:', payload);

      if (callbacks.onAppointmentBooked) {
        const appointment: Appointment = {
          id: payload.appointment_id,
          user_name: payload.user_name,
          contact_number: '',
          appointment_date: payload.date,
          appointment_time: payload.time,
          status: 'active',
          display: payload.display,
        };
        callbacks.onAppointmentBooked(appointment);
      }

      return JSON.stringify({ status: 'received', success: true });
    } catch (error) {
      console.error('Error handling appointment_booked RPC:', error);
      return JSON.stringify({ status: 'error', message: String(error) });
    }
  });

  // Handle appointment cancelled
  localParticipant.registerRpcMethod(
    'appointment_cancelled',
    async (data: RpcInvocationData) => {
      try {
        const payload = JSON.parse(data.payload);
        console.log('Appointment cancelled:', payload);

        if (callbacks.onAppointmentCancelled) {
          callbacks.onAppointmentCancelled(payload);
        }

        return JSON.stringify({ status: 'received', success: true });
      } catch (error) {
        console.error('Error handling appointment_cancelled RPC:', error);
        return JSON.stringify({ status: 'error', message: String(error) });
      }
    }
  );

  // Handle appointment modified
  localParticipant.registerRpcMethod('appointment_modified', async (data: RpcInvocationData) => {
    try {
      const payload = JSON.parse(data.payload);
      console.log('Appointment modified:', payload);

      if (callbacks.onAppointmentModified) {
        callbacks.onAppointmentModified(payload);
      }

      return JSON.stringify({ status: 'received', success: true });
    } catch (error) {
      console.error('Error handling appointment_modified RPC:', error);
      return JSON.stringify({ status: 'error', message: String(error) });
    }
  });

  // Handle conversation summary
  localParticipant.registerRpcMethod('conversation_summary', async (data: RpcInvocationData) => {
    try {
      const payload = JSON.parse(data.payload);
      console.log('Conversation summary received:', payload);

      if (callbacks.onConversationSummary) {
        callbacks.onConversationSummary(payload as ConversationSummary);
      }

      return JSON.stringify({ status: 'received', success: true });
    } catch (error) {
      console.error('Error handling conversation_summary RPC:', error);
      return JSON.stringify({ status: 'error', message: String(error) });
    }
  });

  // Handle tool call updates (optional - for real-time feedback)
  localParticipant.registerRpcMethod('tool_call_update', async (data: RpcInvocationData) => {
    try {
      const payload = JSON.parse(data.payload);
      console.log('Tool call update:', payload);

      if (callbacks.onToolCallUpdate) {
        callbacks.onToolCallUpdate(payload);
      }

      return JSON.stringify({ status: 'received', success: true });
    } catch (error) {
      console.error('Error handling tool_call_update RPC:', error);
      return JSON.stringify({ status: 'error', message: String(error) });
    }
  });

  console.log('RPC handlers registered successfully');
}

export function unregisterRpcHandlers(localParticipant: LocalParticipant) {
  try {
    localParticipant.unregisterRpcMethod('appointment_booked');
    localParticipant.unregisterRpcMethod('appointment_cancelled');
    localParticipant.unregisterRpcMethod('appointment_modified');
    localParticipant.unregisterRpcMethod('conversation_summary');
    localParticipant.unregisterRpcMethod('tool_call_update');
    console.log('RPC handlers unregistered');
  } catch (error) {
    console.error('Error unregistering RPC handlers:', error);
  }
}
