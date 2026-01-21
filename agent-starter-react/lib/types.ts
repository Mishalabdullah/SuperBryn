// Type definitions for the appointment booking agent

export interface Appointment {
  id: string;
  user_name: string;
  contact_number: string;
  appointment_date: string;
  appointment_time: string;
  status: 'active' | 'cancelled' | 'modified';
  created_at?: string;
  updated_at?: string;
  notes?: string;
  display?: string;
}

export interface ToolCall {
  id: string;
  name: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  timestamp: number;
  result?: unknown;
  error?: string;
}

export interface ConversationSummary {
  summary: string;
  appointments: Appointment[];
  costs?: CostBreakdown;
  user?: UserProfile;
}

export interface CostBreakdown {
  llm_cost: number;
  tts_cost: number;
  stt_cost: number;
  total_cost: number;
  // Optional detailed metrics
  completion_tokens?: number;
  prompt_tokens?: number;
  prompt_cached_tokens?: number;
  total_tokens?: number;
  tts_characters?: number;
  tts_audio_duration?: number;
  stt_audio_duration?: number;
}

export interface UserProfile {
  contact_number: string;
  name?: string;
  email?: string;
  is_new?: boolean;
}

export interface SessionState {
  identifiedUser: UserProfile | null;
  appointments: Appointment[];
  toolCalls: ToolCall[];
  summary: ConversationSummary | null;
}

export interface RPCEvent {
  type:
    | 'appointment_booked'
    | 'appointment_cancelled'
    | 'appointment_modified'
    | 'conversation_summary'
    | 'tool_call_update';
  data: unknown;
}
