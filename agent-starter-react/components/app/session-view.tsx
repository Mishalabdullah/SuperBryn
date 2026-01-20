'use client';

import React, { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { toast } from 'sonner';
import { useSessionContext, useSessionMessages } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import {
  AgentControlBar,
  type AgentControlBarControls,
} from '@/components/agents-ui/agent-control-bar';
import { AppointmentList } from '@/components/app/appointment-card';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { SummaryModal } from '@/components/app/summary-modal';
import { TileLayout } from '@/components/app/tile-layout';
import { ToolCallDisplay } from '@/components/app/tool-call-display';
import { registerRpcHandlers, unregisterRpcHandlers } from '@/lib/rpc-handlers';
import { useSessionState } from '@/lib/session-state';
import { cn } from '@/lib/shadcn/utils';
import { Shimmer } from '../ai-elements/shimmer';

const MotionBottom = motion.create('div');

const MotionMessage = motion.create(Shimmer);

const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut',
  },
};

const SHIMMER_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      transition: {
        ease: 'easeIn',
        duration: 0.5,
        delay: 0.8,
      },
    },
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeIn',
        duration: 0.5,
        delay: 0,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  const session = useSessionContext();
  const { messages } = useSessionMessages(session);
  const [chatOpen, setChatOpen] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Session state for appointments, tool calls, and summary
  const {
    state: sessionState,
    addAppointment,
    updateAppointment,
    setSummary,
    addToolCall,
    updateToolCall,
  } = useSessionState();

  const controls: AgentControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsScreenShare,
  };

  // Register RPC handlers when local participant is available
  useEffect(() => {
    const localParticipant = session.room?.localParticipant;
    if (!localParticipant) return;

    console.log('Registering RPC handlers with local participant');

    registerRpcHandlers(localParticipant, {
      onAppointmentBooked: (appointment) => {
        console.log('Appointment booked via RPC:', appointment);
        addAppointment(appointment);
        toast.success('Appointment Booked', {
          description: `${appointment.user_name} - ${appointment.display}`,
        });
      },
      onAppointmentCancelled: (data) => {
        console.log('Appointment cancelled via RPC:', data);
        updateAppointment(data.appointment_id, { status: 'cancelled' });
        toast.error('Appointment Cancelled', {
          description: `${data.user_name} - ${data.display}`,
        });
      },
      onAppointmentModified: (data) => {
        console.log('Appointment modified via RPC:', data);
        updateAppointment(data.appointment_id, {
          appointment_date: data.new_date,
          appointment_time: data.new_time,
          status: 'active',
          display: data.display,
        });
        toast.info('Appointment Rescheduled', {
          description: `${data.user_name} - ${data.display}`,
        });
      },
      onConversationSummary: (summary) => {
        console.log('Conversation summary received via RPC:', summary);
        setSummary(summary);
        setShowSummary(true);
      },
      onToolCallUpdate: (data) => {
        console.log('Tool call update via RPC:', data);
        // You can track tool calls here if needed
      },
    });

    return () => {
      if (localParticipant) {
        unregisterRpcHandlers(localParticipant);
      }
    };
  }, [session.room?.localParticipant, addAppointment, updateAppointment, setSummary]);

  useEffect(() => {
    const lastMessage = messages.at(-1);
    const lastMessageIsLocal = lastMessage?.from?.isLocal === true;

    if (scrollAreaRef.current && lastMessageIsLocal) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section className="bg-background relative z-10 h-svh w-svw overflow-hidden" {...props}>
      <Fade top className="absolute inset-x-4 top-0 z-10 h-40" />

      {/* Appointments Sidebar */}
      {sessionState.appointments.length > 0 && (
        <div className="custom-scrollbar fixed top-20 right-4 z-40 max-h-[calc(100vh-8rem)] w-80 overflow-y-auto md:w-96">
          <div className="border-border bg-card rounded-lg border p-4">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-semibold">Appointments</h3>
              <span className="text-muted-foreground text-xs">
                {sessionState.appointments.length}
              </span>
            </div>
            <AppointmentList appointments={sessionState.appointments} />
          </div>
        </div>
      )}

      {/* Tool Calls Display */}
      <div className="fixed top-4 left-4 z-40 w-80">
        <ToolCallDisplay toolCalls={sessionState.toolCalls} />
      </div>

      {/* Transcript */}
      <ChatTranscript
        hidden={!chatOpen}
        messages={messages}
        className="space-y-3 transition-opacity duration-300 ease-out"
      />

      {/* Tile layout (avatar video) */}
      <TileLayout chatOpen={chatOpen} />

      {/* Bottom Control Bar */}
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="fixed inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {/* Pre-connect message */}
        {appConfig.isPreConnectBufferEnabled && (
          <AnimatePresence>
            {messages.length === 0 && (
              <MotionMessage
                key="pre-connect-message"
                duration={2}
                aria-hidden={messages.length > 0}
                {...SHIMMER_MOTION_PROPS}
                className="pointer-events-none mx-auto block w-full max-w-2xl pb-4 text-center"
              >
                <div className="border-border bg-card rounded-lg border px-6 py-4">
                  <p className="text-foreground text-sm font-medium">Agent is listening...</p>
                  <p className="text-muted-foreground mt-1 text-xs">
                    Ask to book, modify, or cancel an appointment
                  </p>
                </div>
              </MotionMessage>
            )}
          </AnimatePresence>
        )}
        <div className="bg-background relative mx-auto max-w-2xl pb-3 md:pb-12">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          <AgentControlBar
            variant="default"
            controls={controls}
            isChatOpen={chatOpen}
            isConnected={session.isConnected}
            onDisconnect={session.end}
            onIsChatOpenChange={setChatOpen}
          />
        </div>
      </MotionBottom>

      {/* Summary Modal */}
      <SummaryModal
        summary={sessionState.summary}
        isOpen={showSummary}
        onClose={() => setShowSummary(false)}
      />
    </section>
  );
};
