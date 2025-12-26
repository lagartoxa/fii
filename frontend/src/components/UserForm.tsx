import React, { useState, FormEvent, useEffect } from 'react';
import { CreateUserData } from '../services/userService';
import { Role } from '../services/roleService';
import '../styles/fii-form.css';

interface UserFormProps {
    onSubmit: (data: any) => Promise<void>;
    onCancel: () => void;
    isLoading?: boolean;
    initialData?: any;
    isEditMode?: boolean;
    roles: Role[];
}

const UserForm: React.FC<UserFormProps> = ({
    onSubmit,
    onCancel,
    isLoading = false,
    initialData,
    isEditMode = false,
    roles
}) => {
    const [formData, setFormData] = useState<any>({
        email: '',
        username: '',
        full_name: '',
        password: '',
        is_active: true,
        role_pks: []
    });
    const [errors, setErrors] = useState<Record<string, string>>({});

    useEffect(() => {
        if (initialData) {
            setFormData({
                email: initialData.email || '',
                username: initialData.username || '',
                full_name: initialData.full_name || '',
                password: '', // Always empty for security
                is_active: initialData.is_active !== undefined ? initialData.is_active : true,
                role_pks: initialData.role_pks || []
            });
        }
    }, [initialData]);

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.email.trim()) {
            newErrors.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            newErrors.email = 'Invalid email format';
        }

        if (!formData.username.trim()) {
            newErrors.username = 'Username is required';
        } else if (formData.username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
        }

        if (!isEditMode && !formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password && formData.password.length < 8) {
            newErrors.password = 'Password must be at least 8 characters';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        const dataToSubmit: CreateUserData = {
            email: formData.email,
            username: formData.username,
            full_name: formData.full_name || undefined,
            password: formData.password,
            role_pks: formData.role_pks
        };

        // Don't send password if empty in edit mode
        if (isEditMode && !formData.password) {
            delete (dataToSubmit as any).password;
        }

        await onSubmit(dataToSubmit);
    };

    const handleChange = (field: keyof CreateUserData, value: any) => {
        setFormData({ ...formData, [field]: value });
        if (errors[field]) {
            setErrors({ ...errors, [field]: '' });
        }
    };

    const handleRoleToggle = (rolePk: number) => {
        const currentPks = formData.role_pks || [];
        const newPks = currentPks.includes(rolePk)
            ? currentPks.filter((pk: number) => pk !== rolePk)
            : [...currentPks, rolePk];

        handleChange('role_pks', newPks);
    };

    const handleSelectAll = () => {
        const allPks = roles.map(r => r.pk);
        handleChange('role_pks', allPks);
    };

    const handleDeselectAll = () => {
        handleChange('role_pks', []);
    };

    return (
        <form onSubmit={handleSubmit} className="fii-form">
            <div className="form-group">
                <label htmlFor="email">
                    Email <span className="required">*</span>
                </label>
                <input
                    type="email"
                    id="email"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    disabled={isLoading}
                    placeholder="user@example.com"
                    maxLength={255}
                    className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="username">
                    Username <span className="required">*</span>
                </label>
                <input
                    type="text"
                    id="username"
                    value={formData.username}
                    onChange={(e) => handleChange('username', e.target.value)}
                    disabled={isLoading}
                    placeholder="username"
                    maxLength={100}
                    className={errors.username ? 'error' : ''}
                />
                {errors.username && <span className="error-text">{errors.username}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="full_name">Full Name</label>
                <input
                    type="text"
                    id="full_name"
                    value={formData.full_name}
                    onChange={(e) => handleChange('full_name', e.target.value)}
                    disabled={isLoading}
                    placeholder="John Doe"
                    maxLength={255}
                />
            </div>

            <div className="form-group">
                <label htmlFor="password">
                    Password {!isEditMode && <span className="required">*</span>}
                </label>
                <input
                    type="password"
                    id="password"
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    disabled={isLoading}
                    placeholder={isEditMode ? 'Leave empty to keep current password' : 'Min 8 characters'}
                    className={errors.password ? 'error' : ''}
                />
                {errors.password && <span className="error-text">{errors.password}</span>}
                {isEditMode && <span className="help-text">Leave empty to keep current password</span>}
            </div>

            {isEditMode && (
                <div className="form-group">
                    <label htmlFor="is_active" className="switch-label">
                        <span>Active</span>
                        <label className="switch">
                            <input
                                type="checkbox"
                                id="is_active"
                                checked={formData.is_active}
                                onChange={(e) => handleChange('is_active', e.target.checked)}
                                disabled={isLoading}
                            />
                            <span className="slider"></span>
                        </label>
                    </label>
                </div>
            )}

            <div className="form-group">
                <label>
                    Roles
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
                    {roles.map(role => (
                        <label key={role.pk} className="permission-checkbox">
                            <input
                                type="checkbox"
                                checked={(formData.role_pks || []).includes(role.pk)}
                                onChange={() => handleRoleToggle(role.pk)}
                                disabled={isLoading}
                            />
                            <span className="permission-label">
                                <strong>{role.name}</strong>
                                {role.description && (
                                    <span className="permission-description">{role.description}</span>
                                )}
                            </span>
                        </label>
                    ))}
                </div>
                <span className="help-text">
                    {(formData.role_pks || []).length} role(s) selected
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

export default UserForm;
