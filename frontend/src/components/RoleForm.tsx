import React, { useState, FormEvent, useEffect } from 'react';
import { CreateRoleData } from '../services/roleService';
import { Permission } from '../services/permissionService';
import '../styles/fii-form.css';

interface RoleFormProps {
    onSubmit: (data: CreateRoleData) => Promise<void>;
    onCancel: () => void;
    isLoading?: boolean;
    initialData?: CreateRoleData;
    permissions: Permission[];
}

const RoleForm: React.FC<RoleFormProps> = ({
    onSubmit,
    onCancel,
    isLoading = false,
    initialData,
    permissions
}) => {
    const [formData, setFormData] = useState<CreateRoleData>({
        name: '',
        description: '',
        permission_pks: []
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
            description: formData.description || undefined,
            permission_pks: formData.permission_pks
        };

        await onSubmit(dataToSubmit);
    };

    const handleChange = (field: keyof CreateRoleData, value: any) => {
        setFormData({ ...formData, [field]: value });
        if (errors[field]) {
            setErrors({ ...errors, [field]: '' });
        }
    };

    const handlePermissionToggle = (permissionPk: number) => {
        const currentPks = formData.permission_pks || [];
        const newPks = currentPks.includes(permissionPk)
            ? currentPks.filter(pk => pk !== permissionPk)
            : [...currentPks, permissionPk];

        handleChange('permission_pks', newPks);
    };

    const handleSelectAll = () => {
        const allPks = permissions.map(p => p.pk);
        handleChange('permission_pks', allPks);
    };

    const handleDeselectAll = () => {
        handleChange('permission_pks', []);
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

            <div className="form-group">
                <label>
                    Permissions
                    <div className="permission-actions">
                        <button
                            type="button"
                            onClick={handleSelectAll}
                            disabled={isLoading}
                            className="btn-link"
                        >
                            Select All
                        </button>
                        <button
                            type="button"
                            onClick={handleDeselectAll}
                            disabled={isLoading}
                            className="btn-link"
                        >
                            Deselect All
                        </button>
                    </div>
                </label>
                <div className="permission-grid">
                    {permissions.map(permission => (
                        <label key={permission.pk} className="permission-checkbox">
                            <input
                                type="checkbox"
                                checked={(formData.permission_pks || []).includes(permission.pk)}
                                onChange={() => handlePermissionToggle(permission.pk)}
                                disabled={isLoading}
                            />
                            <span className="permission-label">
                                <strong>{permission.resource}</strong>:{permission.action}
                                {permission.description && (
                                    <span className="permission-description">{permission.description}</span>
                                )}
                            </span>
                        </label>
                    ))}
                </div>
                <span className="help-text">
                    {(formData.permission_pks || []).length} permission(s) selected
                </span>
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
