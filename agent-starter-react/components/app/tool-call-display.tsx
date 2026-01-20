'use client';

import React from 'react';
import { CheckCircle, Clock, Loader2, XCircle } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';
import type { ToolCall } from '@/lib/types';

interface ToolCallDisplayProps {
  toolCalls: ToolCall[];
  className?: string;
}

const ToolCallItem = ({ toolCall }: { toolCall: ToolCall }) => {
  const getStatusIcon = () => {
    switch (toolCall.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'in_progress':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusLabel = () => {
    switch (toolCall.name) {
      case 'identify_user':
        return toolCall.status === 'in_progress' ? 'Identifying user...' : 'User identified';
      case 'fetch_slots':
        return toolCall.status === 'in_progress' ? 'Checking availability...' : 'Slots retrieved';
      case 'book_appointment':
        return toolCall.status === 'in_progress' ? 'Booking appointment...' : 'Appointment booked';
      case 'retrieve_appointments':
        return toolCall.status === 'in_progress'
          ? 'Fetching appointments...'
          : 'Appointments retrieved';
      case 'cancel_appointment':
        return toolCall.status === 'in_progress'
          ? 'Cancelling appointment...'
          : 'Appointment cancelled';
      case 'modify_appointment':
        return toolCall.status === 'in_progress'
          ? 'Modifying appointment...'
          : 'Appointment modified';
      case 'end_conversation':
        return toolCall.status === 'in_progress' ? 'Generating summary...' : 'Summary ready';
      default:
        return toolCall.name;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={cn(
        'flex items-center gap-3 rounded-lg border px-4 py-3',
        toolCall.status === 'completed' &&
          'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950',
        toolCall.status === 'error' &&
          'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950',
        toolCall.status === 'in_progress' &&
          'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950',
        toolCall.status === 'pending' &&
          'border-gray-200 bg-gray-50 dark:border-gray-800 dark:bg-gray-950'
      )}
    >
      <div className="flex-shrink-0">{getStatusIcon()}</div>
      <div className="flex-1">
        <p className="text-sm font-medium">{getStatusLabel()}</p>
        {toolCall.error && (
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">{toolCall.error}</p>
        )}
      </div>
    </motion.div>
  );
};

export function ToolCallDisplay({ toolCalls, className }: ToolCallDisplayProps) {
  // Only show recent and active tool calls (last 5 or in-progress)
  const visibleToolCalls = toolCalls
    .filter((tc) => tc.status === 'in_progress' || Date.now() - tc.timestamp < 10000) // Show for 10 seconds after completion
    .slice(-5);

  if (visibleToolCalls.length === 0) {
    return null;
  }

  return (
    <div className={cn('space-y-2', className)}>
      <AnimatePresence mode="popLayout">
        {visibleToolCalls.map((toolCall) => (
          <ToolCallItem key={toolCall.id} toolCall={toolCall} />
        ))}
      </AnimatePresence>
    </div>
  );
}
