import React, { useState, FormEvent, useEffect } from 'react';
import { CreatePermissionData } from '../services/permissionService';
import '../styles/fii-form.css';

interface PermissionFormProps {
    onSubmit: (data: CreatePermissionData) => Promise<void>;
    onCancel: () => void;
    isLoading?: boolean;
    initialData?: CreatePermissionData;
}

const PermissionForm: React.FC<PermissionFormProps> = ({
    onSubmit,
    onCancel,
    isLoading = false,
    initialData
}) => {
    const [formData, setFormData] = useState<CreatePermissionData>({
        resource: '',
        action: '',
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

        if (!formData.resource.trim()) {
            newErrors.resource = 'Resource is required';
        }

        if (!formData.action.trim()) {
            newErrors.action = 'Action is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        const dataToSubmit: CreatePermissionData = {
            resource: formData.resource,
            action: formData.action,
            description: formData.description || undefined
        };

        await onSubmit(dataToSubmit);
    };

    const handleChange = (field: keyof CreatePermissionData, value: string) => {
        setFormData({ ...formData, [field]: value });
        if (errors[field]) {
            setErrors({ ...errors, [field]: '' });
        }
    };

    return (
        <form onSubmit={handleSubmit} className="fii-form">
            <div className="form-group">
                <label htmlFor="resource">
                    Resource <span className="required">*</span>
                </label>
                <input
                    type="text"
                    id="resource"
                    value={formData.resource}
                    onChange={(e) => handleChange('resource', e.target.value)}
                    disabled={isLoading}
                    placeholder="e.g., user, fii, transaction"
                    maxLength={100}
                    className={errors.resource ? 'error' : ''}
                />
                {errors.resource && <span className="error-text">{errors.resource}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="action">
                    Action <span className="required">*</span>
                </label>
                <select
                    id="action"
                    value={formData.action}
                    onChange={(e) => handleChange('action', e.target.value)}
                    disabled={isLoading}
                    className={errors.action ? 'error' : ''}
                >
                    <option value="">Select Action</option>
                    <option value="create">Create</option>
                    <option value="read">Read</option>
                    <option value="update">Update</option>
                    <option value="delete">Delete</option>
                    <option value="list">List</option>
                    <option value="export">Export</option>
                </select>
                {errors.action && <span className="error-text">{errors.action}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleChange('description', e.target.value)}
                    disabled={isLoading}
                    placeholder="Description of the permission"
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

export default PermissionForm;
