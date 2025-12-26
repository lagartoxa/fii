import React, { useState, FormEvent, useEffect } from 'react';
import { CreateDividendData } from '../services/dividendService';
import { FII } from '../services/fiiService';
import DateInput from './DateInput';
import '../styles/fii-form.css';

interface DividendFormProps {
    onSubmit: (data: CreateDividendData) => Promise<void>;
    onCancel: () => void;
    isLoading?: boolean;
    initialData?: CreateDividendData;
    fiis: FII[];
}

const DividendForm: React.FC<DividendFormProps> = ({
    onSubmit,
    onCancel,
    isLoading = false,
    initialData,
    fiis
}) => {
    const [formData, setFormData] = useState<CreateDividendData>({
        fii_pk: 0,
        payment_date: '',
        amount_per_unit: 0,
        com_date: ''
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    // Local state for input values to preserve typing state
    const [amountInput, setAmountInput] = useState<string>('');

    useEffect(() => {
        if (initialData) {
            setFormData(initialData);
            setAmountInput(initialData.amount_per_unit ? String(initialData.amount_per_unit) : '');
        }
    }, [initialData]);

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.fii_pk || formData.fii_pk === 0) {
            newErrors.fii_pk = 'FII is required';
        }

        if (!formData.payment_date) {
            newErrors.payment_date = 'Payment date is required';
        }

        if (formData.amount_per_unit <= 0) {
            newErrors.amount_per_unit = 'Amount per unit must be greater than 0';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        const dataToSubmit: CreateDividendData = {
            fii_pk: formData.fii_pk,
            payment_date: formData.payment_date,
            amount_per_unit: formData.amount_per_unit,
            com_date: formData.com_date
        };

        await onSubmit(dataToSubmit);
    };

    const handleChange = (field: keyof CreateDividendData, value: any) => {
        setFormData({ ...formData, [field]: value });
        if (errors[field]) {
            setErrors({ ...errors, [field]: '' });
        }
    };

    return (
        <form onSubmit={handleSubmit} className="fii-form">
            <div className="form-group">
                <label htmlFor="fii_pk">
                    FII <span className="required">*</span>
                </label>
                <select
                    id="fii_pk"
                    value={formData.fii_pk}
                    onChange={(e) => handleChange('fii_pk', parseInt(e.target.value))}
                    disabled={isLoading}
                    className={errors.fii_pk ? 'error' : ''}
                >
                    <option value={0}>Select FII</option>
                    {fiis.map(fii => (
                        <option key={fii.pk} value={fii.pk}>
                            {fii.tag} - {fii.name}
                        </option>
                    ))}
                </select>
                {errors.fii_pk && <span className="error-text">{errors.fii_pk}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="payment_date">
                    Payment Date <span className="required">*</span>
                </label>
                <DateInput
                    id="payment_date"
                    value={formData.payment_date}
                    onChange={(value) => handleChange('payment_date', value)}
                    disabled={isLoading}
                    className={errors.payment_date ? 'error' : ''}
                    required
                />
                {errors.payment_date && <span className="error-text">{errors.payment_date}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="amount_per_unit">
                    Amount per Unit <span className="required">*</span>
                </label>
                <input
                    type="text"
                    inputMode="decimal"
                    id="amount_per_unit"
                    value={amountInput}
                    onChange={(e) => {
                        const value = e.target.value;
                        // Allow empty, digits, and one decimal point
                        if (value === '' || /^[0-9]*\.?[0-9]*$/.test(value)) {
                            setAmountInput(value);

                            // Update form data with numeric value
                            if (value === '' || value === '.') {
                                handleChange('amount_per_unit', 0);
                            } else {
                                const numValue = parseFloat(value);
                                handleChange('amount_per_unit', isNaN(numValue) ? 0 : numValue);
                            }
                        }
                    }}
                    onBlur={() => {
                        // Clean up on blur - if there's a valid number, format it
                        if (formData.amount_per_unit > 0) {
                            setAmountInput(String(formData.amount_per_unit));
                        } else {
                            setAmountInput('');
                        }
                    }}
                    disabled={isLoading}
                    placeholder="0.0000"
                    className={errors.amount_per_unit ? 'error' : ''}
                />
                {errors.amount_per_unit && <span className="error-text">{errors.amount_per_unit}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="com_date">
                    Data COM
                </label>
                <DateInput
                    id="com_date"
                    value={formData.com_date || ''}
                    onChange={(value) => handleChange('com_date', value)}
                    disabled={isLoading}
                    className={errors.com_date ? 'error' : ''}
                />
                <span className="help-text">Data de corte para elegibilidade do dividendo</span>
                {errors.com_date && <span className="error-text">{errors.com_date}</span>}
            </div>

            <div className="form-actions">
                <button
                    type="button"
                    onClick={onCancel}
                    className="btn-secondary"
                    disabled={isLoading}
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    className="btn-primary"
                    disabled={isLoading}
                >
                    {isLoading ? 'Saving...' : 'Save'}
                </button>
            </div>
        </form>
    );
};

export default DividendForm;
