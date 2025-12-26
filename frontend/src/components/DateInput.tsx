import React from 'react';
import DatePicker from 'react-datepicker';
import { parse, format, isValid } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import '../styles/datepicker.css';

interface DateInputProps {
    id: string;
    value: string; // YYYY-MM-DD format string
    onChange: (value: string) => void;
    disabled?: boolean;
    className?: string;
    placeholder?: string;
    required?: boolean;
}

const DateInput: React.FC<DateInputProps> = ({
    id,
    value,
    onChange,
    disabled = false,
    className = '',
    placeholder = 'dd/mm/aaaa',
    required = false
}) => {
    // Convert YYYY-MM-DD string to Date object
    const parseDate = (dateString: string): Date | null => {
        if (!dateString) return null;

        const parsedDate = parse(dateString, 'yyyy-MM-dd', new Date());
        return isValid(parsedDate) ? parsedDate : null;
    };

    // Convert Date object to YYYY-MM-DD string
    const formatDate = (date: Date | null): string => {
        if (!date || !isValid(date)) return '';
        return format(date, 'yyyy-MM-dd');
    };

    const selectedDate = parseDate(value);

    const handleChange = (date: Date | null) => {
        const formattedDate = formatDate(date);
        onChange(formattedDate);
    };

    return (
        <DatePicker
            id={id}
            selected={selectedDate}
            onChange={handleChange}
            dateFormat="dd/MM/yyyy"
            locale={ptBR}
            disabled={disabled}
            placeholderText={placeholder}
            required={required}
            className={`date-input ${className}`}
            wrapperClassName="date-input-wrapper"
            calendarClassName="date-input-calendar"
            showYearDropdown
            showMonthDropdown
            dropdownMode="select"
            autoComplete="off"
        />
    );
};

export default DateInput;
