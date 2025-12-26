import React, { useState, FormEvent, useEffect } from 'react';
import { CreateTransactionData } from '../services/transactionService';
import { FII } from '../services/fiiService';
import DateInput from './DateInput';
import '../styles/fii-form.css';

interface TransactionFormProps {
    onSubmit: (data: CreateTransactionData) => Promise<void>;
    onCancel: () => void;
    isLoading?: boolean;
    initialData?: CreateTransactionData;
    fiis: FII[];
}

const TransactionForm: React.FC<TransactionFormProps> = ({
    onSubmit,
    onCancel,
    isLoading = false,
    initialData,
    fiis
}) => {
    const [formData, setFormData] = useState<CreateTransactionData>({
        fii_pk: 0,
        transaction_type: 'buy',
        transaction_date: '',
        quantity: 0,
        price_per_unit: 0,
        total_amount: 0
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    // Local state for input values to preserve typing state
    const [priceInput, setPriceInput] = useState<string>('');

    useEffect(() => {
        if (initialData) {
            setFormData(initialData);
            setPriceInput(initialData.price_per_unit ? String(initialData.price_per_unit) : '');
        }
    }, [initialData]);

    // Auto-calculate total_amount when quantity or price changes
    useEffect(() => {
        if (formData.quantity > 0 && formData.price_per_unit > 0) {
            const total = formData.quantity * formData.price_per_unit;
            setFormData(prev => ({ ...prev, total_amount: parseFloat(total.toFixed(2)) }));
        }
    }, [formData.quantity, formData.price_per_unit]);

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.fii_pk || formData.fii_pk === 0) {
            newErrors.fii_pk = 'FII is required';
        }

        if (!formData.transaction_date) {
            newErrors.transaction_date = 'Transaction date is required';
        }

        if (formData.quantity <= 0) {
            newErrors.quantity = 'Quantity must be greater than 0';
        }

        if (formData.price_per_unit <= 0) {
            newErrors.price_per_unit = 'Price per unit must be greater than 0';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        await onSubmit(formData);
    };

    const handleChange = (field: keyof CreateTransactionData, value: any) => {
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
                <label htmlFor="transaction_type">
                    Type <span className="required">*</span>
                </label>
                <select
                    id="transaction_type"
                    value={formData.transaction_type}
                    onChange={(e) => handleChange('transaction_type', e.target.value)}
                    disabled={isLoading}
                >
                    <option value="buy">Buy</option>
                    <option value="sell">Sell</option>
                </select>
            </div>

            <div className="form-group">
                <label htmlFor="transaction_date">
                    Date <span className="required">*</span>
                </label>
                <DateInput
                    id="transaction_date"
                    value={formData.transaction_date}
                    onChange={(value) => handleChange('transaction_date', value)}
                    disabled={isLoading}
                    className={errors.transaction_date ? 'error' : ''}
                    required
                />
                {errors.transaction_date && <span className="error-text">{errors.transaction_date}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="quantity">
                    Quantity <span className="required">*</span>
                </label>
                <input
                    type="text"
                    inputMode="numeric"
                    id="quantity"
                    value={formData.quantity === 0 ? '' : formData.quantity}
                    onChange={(e) => {
                        const value = e.target.value;
                        if (value === '' || /^\d+$/.test(value)) {
                            handleChange('quantity', value === '' ? 0 : parseInt(value));
                        }
                    }}
                    disabled={isLoading}
                    placeholder="0"
                    className={errors.quantity ? 'error' : ''}
                />
                {errors.quantity && <span className="error-text">{errors.quantity}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="price_per_unit">
                    Price per Unit <span className="required">*</span>
                </label>
                <input
                    type="text"
                    inputMode="decimal"
                    id="price_per_unit"
                    value={priceInput}
                    onChange={(e) => {
                        const value = e.target.value;
                        // Allow empty, digits, and one decimal point
                        if (value === '' || /^[0-9]*\.?[0-9]*$/.test(value)) {
                            setPriceInput(value);

                            // Update form data with numeric value
                            if (value === '' || value === '.') {
                                handleChange('price_per_unit', 0);
                            } else {
                                const numValue = parseFloat(value);
                                handleChange('price_per_unit', isNaN(numValue) ? 0 : numValue);
                            }
                        }
                    }}
                    onBlur={() => {
                        // Clean up on blur - if there's a valid number, format it
                        if (formData.price_per_unit > 0) {
                            setPriceInput(String(formData.price_per_unit));
                        } else {
                            setPriceInput('');
                        }
                    }}
                    disabled={isLoading}
                    placeholder="0.00"
                    className={errors.price_per_unit ? 'error' : ''}
                />
                {errors.price_per_unit && <span className="error-text">{errors.price_per_unit}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="total_amount">Total Amount</label>
                <input
                    type="text"
                    id="total_amount"
                    value={formData.total_amount === 0 ? '' : Number(formData.total_amount).toFixed(2)}
                    disabled
                />
                <span className="help-text">Auto-calculated from quantity × price</span>
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

export default TransactionForm;
