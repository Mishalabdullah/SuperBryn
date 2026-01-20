'use client';

import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Download, DollarSign } from 'lucide-react';
import type { ConversationSummary } from '@/lib/types';
import { AppointmentList } from './appointment-card';
import { cn } from '@/lib/shadcn/utils';

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
              'fixed left-1/2 top-1/2 z-50 w-full max-w-3xl -translate-x-1/2 -translate-y-1/2',
              'rounded-lg border border-border bg-card p-6',
              className
            )}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-border pb-4 mb-6">
              <h2 className="text-xl font-semibold">Session Summary</h2>
              <div className="flex items-center gap-1">
                <button
                  onClick={handleDownload}
                  className="rounded-md p-2 hover:bg-muted transition-colors"
                  title="Download summary"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button
                  onClick={onClose}
                  className="rounded-md p-2 hover:bg-muted transition-colors"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="space-y-6 max-h-[65vh] overflow-y-auto pr-2 custom-scrollbar">
              {/* Summary Text */}
              <div className="rounded-lg border border-border bg-muted/50 p-4">
                <h3 className="text-sm font-medium mb-2">Summary</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{summary.summary}</p>
              </div>

              {/* Appointments */}
              {summary.appointments && summary.appointments.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-3">Appointments ({summary.appointments.length})</h3>
                  <AppointmentList appointments={summary.appointments} />
                </div>
              )}

              {/* User Info */}
              {summary.user && (
                <div>
                  <h3 className="text-sm font-medium mb-3">User Information</h3>
                  <div className="rounded-lg border border-border bg-muted/50 p-4 space-y-2">
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
                      <div className="pt-2 border-t border-border">
                        <span className="text-xs text-muted-foreground">New user</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Cost Breakdown (Bonus Feature) */}
              {summary.costs && summary.costs.total_cost > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-3">Cost Breakdown</h3>
                  <div className="rounded-lg border border-border bg-muted/50 p-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">LLM</span>
                      <span className="font-mono text-sm">${summary.costs.llm_cost.toFixed(6)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">TTS</span>
                      <span className="font-mono text-sm">${summary.costs.tts_cost.toFixed(6)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">STT</span>
                      <span className="font-mono text-sm">${summary.costs.stt_cost.toFixed(6)}</span>
                    </div>
                    <div className="flex justify-between text-sm font-medium border-t border-border pt-2 mt-2">
                      <span>Total</span>
                      <span className="font-mono">${summary.costs.total_cost.toFixed(6)}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="mt-6 flex justify-end gap-2 border-t border-border pt-4">
              <button
                onClick={handleDownload}
                className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:bg-muted transition-colors flex items-center gap-2"
              >
                <Download className="h-4 w-4" />
                Download
              </button>
              <button
                onClick={onClose}
                className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
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
