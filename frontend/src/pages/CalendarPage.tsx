import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ChevronLeftIcon, ChevronRightIcon,
  CalendarDaysIcon, ClockIcon,
} from '@heroicons/react/24/outline';
import calendarService from '../services/calendarService';

interface CalendarEvent {
  id: number;
  title: string;
  start: string;
  platform: string;
  status: string;
  color: string;
  pillar_name: string;
  pillar_color: string;
}

const PLATFORM_COLORS: Record<string, string> = {
  twitter: '#1DA1F2',
  linkedin: '#0A66C2',
  facebook: '#1877F2',
  instagram: '#E4405F',
};

const STATUS_BADGES: Record<string, string> = {
  draft: 'bg-gray-500/20 text-gray-400',
  pending_approval: 'bg-yellow-500/20 text-yellow-400',
  approved: 'bg-blue-500/20 text-blue-400',
  scheduled: 'bg-purple-500/20 text-purple-400',
  posted: 'bg-green-500/20 text-green-400',
  failed: 'bg-red-500/20 text-red-400',
};

export function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'month' | 'week'>('month');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEvents();
  }, [currentDate, view]);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const start = getViewStart();
      const end = getViewEnd();
      const data = await calendarService.getCalendarEvents(start.toISOString(), end.toISOString());
      setEvents(data);
    } catch (err) {
      console.error('Failed to load calendar events:', err);
    }
    setLoading(false);
  };

  const getViewStart = () => {
    const d = new Date(currentDate);
    if (view === 'month') {
      d.setDate(1);
      d.setDate(d.getDate() - d.getDay());
    } else {
      d.setDate(d.getDate() - d.getDay());
    }
    d.setHours(0, 0, 0, 0);
    return d;
  };

  const getViewEnd = () => {
    const d = getViewStart();
    d.setDate(d.getDate() + (view === 'month' ? 42 : 7));
    return d;
  };

  const navigate = (dir: number) => {
    const d = new Date(currentDate);
    if (view === 'month') {
      d.setMonth(d.getMonth() + dir);
    } else {
      d.setDate(d.getDate() + dir * 7);
    }
    setCurrentDate(d);
  };

  const getDaysInView = () => {
    const start = getViewStart();
    const days: Date[] = [];
    const count = view === 'month' ? 42 : 7;
    for (let i = 0; i < count; i++) {
      const d = new Date(start);
      d.setDate(d.getDate() + i);
      days.push(d);
    }
    return days;
  };

  const getEventsForDay = (date: Date) => {
    return events.filter((e) => {
      const eventDate = new Date(e.start);
      return eventDate.toDateString() === date.toDateString();
    });
  };

  const isToday = (date: Date) => date.toDateString() === new Date().toDateString();
  const isCurrentMonth = (date: Date) => date.getMonth() === currentDate.getMonth();

  const days = getDaysInView();
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  const monthName = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Content Calendar</h1>
          <p className="text-text-secondary mt-1">Schedule and manage your content</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex bg-dark-700 rounded-lg overflow-hidden">
            <button onClick={() => setView('week')} className={`px-3 py-1.5 text-sm ${view === 'week' ? 'bg-primary-500 text-white' : 'text-text-secondary'}`}>Week</button>
            <button onClick={() => setView('month')} className={`px-3 py-1.5 text-sm ${view === 'month' ? 'bg-primary-500 text-white' : 'text-text-secondary'}`}>Month</button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="btn-icon">
          <ChevronLeftIcon className="w-5 h-5" />
        </button>
        <h2 className="text-lg font-semibold">{monthName}</h2>
        <button onClick={() => navigate(1)} className="btn-icon">
          <ChevronRightIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Calendar Grid */}
      <div className="card overflow-hidden">
        {/* Day Headers */}
        <div className="grid grid-cols-7 border-b border-white/10">
          {dayNames.map((d) => (
            <div key={d} className="p-2 text-center text-xs font-medium text-text-secondary">
              {d}
            </div>
          ))}
        </div>

        {/* Days Grid */}
        <div className={`grid grid-cols-7 ${view === 'month' ? '' : ''}`}>
          {days.map((day, idx) => {
            const dayEvents = getEventsForDay(day);
            return (
              <div
                key={idx}
                className={`min-h-[100px] p-1 border-b border-r border-white/5 ${
                  !isCurrentMonth(day) ? 'opacity-40' : ''
                } ${isToday(day) ? 'bg-primary-500/5' : ''}`}
              >
                <div className={`text-xs font-medium mb-1 px-1 ${
                  isToday(day) ? 'text-primary-400' : 'text-text-secondary'
                }`}>
                  {day.getDate()}
                </div>
                <div className="space-y-0.5">
                  {dayEvents.slice(0, 3).map((event, eIdx) => (
                    <div
                      key={eIdx}
                      className="text-[10px] px-1 py-0.5 rounded truncate cursor-pointer hover:opacity-80"
                      style={{ backgroundColor: `${event.color || PLATFORM_COLORS[event.platform] || '#6B7280'}20`, color: event.color || PLATFORM_COLORS[event.platform] || '#6B7280', borderLeft: `2px solid ${event.color || PLATFORM_COLORS[event.platform]}` }}
                      title={`${event.title} (${event.platform})`}
                    >
                      {event.title}
                    </div>
                  ))}
                  {dayEvents.length > 3 && (
                    <div className="text-[10px] text-text-secondary px-1">
                      +{dayEvents.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-text-secondary">
        {Object.entries(PLATFORM_COLORS).map(([platform, color]) => (
          <div key={platform} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: color }} />
            <span className="capitalize">{platform}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CalendarPage;
