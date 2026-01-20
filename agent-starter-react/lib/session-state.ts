import { useCallback, useState } from 'react';
import type {
  Appointment,
  ConversationSummary,
  SessionState,
  ToolCall,
  UserProfile,
} from './types';

export function useSessionState() {
  const [state, setState] = useState<SessionState>({
    identifiedUser: null,
    appointments: [],
    toolCalls: [],
    summary: null,
  });

  const setIdentifiedUser = useCallback((user: UserProfile | null) => {
    setState((prev) => ({ ...prev, identifiedUser: user }));
  }, []);

  const addAppointment = useCallback((appointment: Appointment) => {
    setState((prev) => ({
      ...prev,
      appointments: [appointment, ...prev.appointments],
    }));
  }, []);

  const updateAppointment = useCallback((appointmentId: string, updates: Partial<Appointment>) => {
    setState((prev) => ({
      ...prev,
      appointments: prev.appointments.map((appt) =>
        appt.id === appointmentId ? { ...appt, ...updates } : appt
      ),
    }));
  }, []);

  const removeAppointment = useCallback((appointmentId: string) => {
    setState((prev) => ({
      ...prev,
      appointments: prev.appointments.filter((appt) => appt.id !== appointmentId),
    }));
  }, []);

  const addToolCall = useCallback((toolCall: ToolCall) => {
    setState((prev) => ({
      ...prev,
      toolCalls: [...prev.toolCalls, toolCall],
    }));
  }, []);

  const updateToolCall = useCallback((toolCallId: string, updates: Partial<ToolCall>) => {
    setState((prev) => ({
      ...prev,
      toolCalls: prev.toolCalls.map((tc) => (tc.id === toolCallId ? { ...tc, ...updates } : tc)),
    }));
  }, []);

  const setSummary = useCallback((summary: ConversationSummary) => {
    setState((prev) => ({ ...prev, summary }));
  }, []);

  const reset = useCallback(() => {
    setState({
      identifiedUser: null,
      appointments: [],
      toolCalls: [],
      summary: null,
    });
  }, []);

  return {
    state,
    setIdentifiedUser,
    addAppointment,
    updateAppointment,
    removeAppointment,
    addToolCall,
    updateToolCall,
    setSummary,
    reset,
  };
}
