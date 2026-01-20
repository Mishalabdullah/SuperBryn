'use client';

import React from 'react';
import { motion } from 'motion/react';
import { Calendar, Clock, User, CheckCircle, XCircle } from 'lucide-react';
import type { Appointment } from '@/lib/types';
import { cn } from '@/lib/shadcn/utils';

interface AppointmentCardProps {
  appointment: Appointment;
  className?: string;
}

export function AppointmentCard({ appointment, className }: AppointmentCardProps) {
  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      
      // Validate the date is actually valid
      if (isNaN(date.getTime())) {
        console.warn('Invalid date:', dateStr);
        return dateStr;
      }
      
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch (error) {
      console.error('Error formatting date:', error);
      return dateStr;
    }
  };

  const formatTime = (timeStr: string) => {
    try {
      // timeStr might be "HH:MM:SS" or just "HH:MM"
      const [hours, minutes] = timeStr.split(':');
      const hour = parseInt(hours, 10);
      const isPM = hour >= 12;
      const displayHour = hour % 12 || 12;
      return `${displayHour}:${minutes} ${isPM ? 'PM' : 'AM'}`;
    } catch {
      return timeStr;
    }
  };

  const getStatusIcon = () => {
    switch (appointment.status) {
      case 'active':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'cancelled':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'modified':
        return <CheckCircle className="h-5 w-5 text-blue-500" />;
      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      className={cn(
        'rounded-lg border border-border bg-card p-4 transition-colors hover:bg-muted/50',
        appointment.status === 'cancelled' && 'opacity-50',
        className
      )}
    >
      <div className="space-y-3">
        {/* User Name with Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center">
              <User className="h-3 w-3 text-muted-foreground" />
            </div>
            <span className="font-medium text-sm">{appointment.user_name}</span>
          </div>
          {getStatusIcon()}
        </div>

        {/* Date & Time */}
        <div className="space-y-1.5 text-sm">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="h-3.5 w-3.5" />
            <span>{formatDate(appointment.appointment_date)}</span>
          </div>

          <div className="flex items-center gap-2 text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            <span>{formatTime(appointment.appointment_time)}</span>
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center gap-2 pt-1">
          <div
            className={cn(
              'inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-xs font-medium',
              appointment.status === 'active' &&
                'border-green-500/20 bg-green-500/10 text-green-600 dark:text-green-400',
              appointment.status === 'cancelled' &&
                'border-red-500/20 bg-red-500/10 text-red-600 dark:text-red-400',
              appointment.status === 'modified' &&
                'border-blue-500/20 bg-blue-500/10 text-blue-600 dark:text-blue-400'
            )}
          >
            <span className={cn(
              'w-1 h-1 rounded-full',
              appointment.status === 'active' && 'bg-green-500',
              appointment.status === 'cancelled' && 'bg-red-500',
              appointment.status === 'modified' && 'bg-blue-500'
            )} />
            {appointment.status.charAt(0).toUpperCase() + appointment.status.slice(1)}
          </div>
        </div>

        {/* Notes (if any) */}
        {appointment.notes && (
          <p className="text-xs text-muted-foreground pt-2 border-t border-border">
            {appointment.notes}
          </p>
        )}
      </div>
    </motion.div>
  );
}

interface AppointmentListProps {
  appointments: Appointment[];
  className?: string;
}

export function AppointmentList({ appointments, className }: AppointmentListProps) {
  if (appointments.length === 0) {
    return (
      <div className={cn('text-center text-sm text-muted-foreground py-8', className)}>
        No appointments to display
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      {appointments.map((appointment) => (
        <AppointmentCard key={appointment.id} appointment={appointment} />
      ))}
    </div>
  );
}
