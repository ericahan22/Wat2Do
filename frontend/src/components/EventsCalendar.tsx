import React, { useState } from 'react';
import { Calendar, dateFnsLocalizer, NavigateAction, View } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { enUS } from 'date-fns/locale/en-US';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import '../styles/calendar.css';

const locales = {
    'en-US': enUS,
};

const localizer = dateFnsLocalizer({
    format,
    parse,
    startOfWeek,
    getDay,
    locales
});

interface Event {
    id: string;
    name: string;
    date: string;
    start_time: string;
    end_time: string;
    location: string;
}

interface EventsCalendarProps {
    events: Event[];
}

// Custom toolbar for < and > month buttons
const CustomToolbar: React.FC<{
  label: string;
  onNavigate: (action: 'PREV' | 'NEXT' | 'TODAY') => void;
}> = ({ label, onNavigate }) => {
  return (
    <div className='relative mb-4'>
      {/* Today button */}
      <button
        onClick={() => onNavigate('TODAY')}
        className='absolute left-0 top-1/2 -translate-y-1/2 rbc-btn px-4 py-1 text-sm font-medium text-gray-800 dark:text-gray-200 rounded hover:bg-gray-200 dark:hover:bg-gray-600'
        aria-label='Today'
      >
        Today
      </button>

      <div className='flex items-center justify-center gap-4'>
        {/* Back button < */}
        <button
            onClick={() => onNavigate('PREV')}
            className='text-gray-800 dark:text-gray-200'
            aria-label="Previous Month"
            style={{ padding: '4px 8px' }}
        >
            <ChevronLeft className='h-6 w-6' />
        </button>

        {/* Month Year title */}
        <div className='flex items-center justify-center' style={{ width: '140px' }}>
          <h2 className='text-lg font-bold text-gray-900 dark:text-white'>{label}</h2>
        </div>

        {/* Next button > */}
        <button
            onClick={() => onNavigate('NEXT')}
            className='text-gray-800 dark:text-gray-200'
            aria-label='Next Month'
            style={{ padding: '4px 8px' }}
        >
            <ChevronRight className='h-6 w-6' />
        </button>
      </div>
    </div>
  );
};

const EventsCalendar: React.FC<EventsCalendarProps> = ({ events }) => {
    const [currentDate, setCurrentDate] = useState(new Date());

    const calendarEvents = events.map((event) => ({
        id: event.id,
        title: event.name,
        start: new Date(`${event.date}T${event.start_time}`),
        end: new Date(`${event.date}T${event.end_time}`),
        location: event.location,
    }));

    const handleNavigate = (newDate: Date, _view: View, _action: NavigateAction) => {
       setCurrentDate(newDate);
    };

    return (
        <div className='events-calendar-container'>
            <Calendar
                localizer={localizer}
                events={calendarEvents}
                startAccessor="start"
                endAccessor="end"
                date={currentDate}
                onNavigate={handleNavigate}
                components={{
                    toolbar: CustomToolbar,
                }}
            />
        </div>
    );
};

export default EventsCalendar;
