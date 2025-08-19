import React from 'react';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import { enUS } from 'date-fns/locale/en-US';
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

const EventsCalendar: React.FC<EventsCalendarProps> = ({ events }) => {
    const calendarEvents = events.map((event) => ({
        id: event.id,
        title: event.name,
        start: new Date(`${event.date}T${event.start_time}`),
        end: new Date(`${event.date}T${event.end_time}`),
        location: event.location,
    }));

    return (
        <div className='events-calendar-container'>
            <Calendar
                localizer={localizer}
                events={calendarEvents}
                startAccessor="start"
                endAccessor="end"
            />
        </div>
    );
};

export default EventsCalendar;
