'use client';

import React from 'react';
import { Download, X } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import { cn } from '@/lib/shadcn/utils';
import type { ConversationSummary } from '@/lib/types';
import { AppointmentList } from './appointment-card';

interface SummaryModalProps {
  summary: ConversationSummary | null;
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

export function SummaryModal({ summary, isOpen, onClose, className }: SummaryModalProps) {
  if (!summary) return null;

  const handleDownload = () => {
    const content = `
CONVERSATION SUMMARY
====================

${summary.summary}

${
  summary.appointments && summary.appointments.length > 0
    ? `
APPOINTMENTS
------------
${summary.appointments
  .map(
    (appt, idx) =>
      `${idx + 1}. ${appt.appointment_date} at ${appt.appointment_time} (${appt.status})`
  )
  .join('\n')}
`
    : ''
}

${
  summary.user
    ? `
USER INFORMATION
----------------
Name: ${summary.user.name || 'Not provided'}
Phone: ${summary.user.contact_number}
`
    : ''
}

${
  summary.costs
    ? `
COST BREAKDOWN
--------------
LLM: $${summary.costs.llm_cost.toFixed(6)}
TTS: $${summary.costs.tts_cost.toFixed(6)}
STT: $${summary.costs.stt_cost.toFixed(6)}
Total: $${summary.costs.total_cost.toFixed(6)}
`
    : ''
}

Generated: ${new Date().toLocaleString()}
`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversation-summary-${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.98, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.98, y: 8 }}
            className={cn(
              'fixed top-1/2 left-1/2 z-50 w-full max-w-3xl -translate-x-1/2 -translate-y-1/2',
              'border-border bg-card rounded-lg border p-6',
              className
            )}
          >
            {/* Header */}
            <div className="border-border mb-6 flex items-center justify-between border-b pb-4">
              <h2 className="text-xl font-semibold">Session Summary</h2>
              <div className="flex items-center gap-1">
                <button
                  onClick={handleDownload}
                  className="hover:bg-muted rounded-md p-2 transition-colors"
                  title="Download summary"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button
                  onClick={onClose}
                  className="hover:bg-muted rounded-md p-2 transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="custom-scrollbar max-h-[65vh] space-y-6 overflow-y-auto pr-2">
              {/* Summary Text */}
              <div className="border-border bg-muted/50 rounded-lg border p-4">
                <h3 className="mb-2 text-sm font-medium">Summary</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{summary.summary}</p>
              </div>

              {/* Appointments */}
              {summary.appointments && summary.appointments.length > 0 && (
                <div>
                  <h3 className="mb-3 text-sm font-medium">
                    Appointments ({summary.appointments.length})
                  </h3>
                  <AppointmentList appointments={summary.appointments} />
                </div>
              )}

              {/* User Info */}
              {summary.user && (
                <div>
                  <h3 className="mb-3 text-sm font-medium">User Information</h3>
                  <div className="border-border bg-muted/50 space-y-2 rounded-lg border p-4">
                    {summary.user.name && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Name</span>
                        <span className="font-medium">{summary.user.name}</span>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Phone</span>
                      <span className="font-mono text-sm">{summary.user.contact_number}</span>
                    </div>
                    {summary.user.is_new && (
                      <div className="border-border border-t pt-2">
                        <span className="text-muted-foreground text-xs">New user</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Cost Breakdown (Bonus Feature) */}
              {summary.costs && summary.costs.total_cost > 0 && (
                <div>
                  <h3 className="mb-3 text-sm font-medium">Cost Breakdown</h3>
                  <div className="border-border bg-muted/50 space-y-2 rounded-lg border p-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">LLM</span>
                      <span className="font-mono text-sm">
                        ${summary.costs.llm_cost.toFixed(6)}
                      </span>
                    </div>
                    {summary.costs.total_tokens && summary.costs.total_tokens > 0 && (
                      <div className="text-muted-foreground ml-4 flex justify-between text-xs">
                        <span>
                          {summary.costs.prompt_tokens?.toLocaleString()} prompt +{' '}
                          {summary.costs.completion_tokens?.toLocaleString()} completion
                          {summary.costs.prompt_cached_tokens &&
                            summary.costs.prompt_cached_tokens > 0 && (
                              <span className="text-green-600">
                                {' '}
                                ({summary.costs.prompt_cached_tokens} cached)
                              </span>
                            )}
                        </span>
                        <span>{summary.costs.total_tokens.toLocaleString()} tokens</span>
                      </div>
                    )}
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">TTS</span>
                      <span className="font-mono text-sm">
                        ${summary.costs.tts_cost.toFixed(6)}
                      </span>
                    </div>
                    {summary.costs.tts_characters && summary.costs.tts_characters > 0 && (
                      <div className="text-muted-foreground ml-4 flex justify-between text-xs">
                        <span>{summary.costs.tts_characters.toLocaleString()} characters</span>
                        {summary.costs.tts_audio_duration && (
                          <span>{summary.costs.tts_audio_duration.toFixed(1)}s audio</span>
                        )}
                      </div>
                    )}
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">STT</span>
                      <span className="font-mono text-sm">
                        ${summary.costs.stt_cost.toFixed(6)}
                      </span>
                    </div>
                    {summary.costs.stt_audio_duration && summary.costs.stt_audio_duration > 0 && (
                      <div className="text-muted-foreground ml-4 flex justify-between text-xs">
                        <span>{summary.costs.stt_audio_duration.toFixed(1)}s audio</span>
                        <span>{(summary.costs.stt_audio_duration / 60).toFixed(2)} min</span>
                      </div>
                    )}
                    <div className="border-border mt-2 flex justify-between border-t pt-2 text-sm font-medium">
                      <span>Total</span>
                      <span className="font-mono">${summary.costs.total_cost.toFixed(6)}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="border-border mt-6 flex justify-end gap-2 border-t pt-4">
              <button
                onClick={handleDownload}
                className="border-border hover:bg-muted flex items-center gap-2 rounded-md border px-4 py-2 text-sm font-medium transition-colors"
              >
                <Download className="h-4 w-4" />
                Download
              </button>
              <button
                onClick={onClose}
                className="bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2 text-sm font-medium transition-colors"
              >
                Close
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
