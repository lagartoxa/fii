import React, { useState, FormEvent, useEffect } from 'react';
import { CreateRoleData } from '../services/roleService';
import '../styles/fii-form.css';

interface RoleFormProps {
    onSubmit: (data: CreateRoleData) => Promise<void>;
    onCancel: () => void;
    isLoading?: boolean;
    initialData?: CreateRoleData;
}

const RoleForm: React.FC<RoleFormProps> = ({
    onSubmit,
    onCancel,
    isLoading = false,
    initialData
}) => {
    const [formData, setFormData] = useState<CreateRoleData>({
        name: '',
        description: ''
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (initialData) {
            setFormData(initialData);
        }
    }, [initialData]);

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.name.trim()) {
            newErrors.name = 'Name is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        const dataToSubmit: CreateRoleData = {
            name: formData.name,
            description: formData.description || undefined
        };

        await onSubmit(dataToSubmit);
    };

    const handleChange = (field: keyof CreateRoleData, value: string) => {
        setFormData({ ...formData, [field]: value });
        if (errors[field]) {
            setErrors({ ...errors, [field]: '' });
        }
    };

    return (
        <form onSubmit={handleSubmit} className="fii-form">
            <div className="form-group">
                <label htmlFor="name">
                    Name <span className="required">*</span>
                </label>
                <input
                    type="text"
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    disabled={isLoading}
                    placeholder="e.g., admin, user, viewer"
                    maxLength={50}
                    className={errors.name ? 'error' : ''}
                />
                {errors.name && <span className="error-text">{errors.name}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleChange('description', e.target.value)}
                    disabled={isLoading}
                    placeholder="Description of the role"
                    maxLength={255}
                    rows={3}
                />
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

export default RoleForm;
