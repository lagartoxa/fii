import React, { useState, useEffect } from 'react';
import roleService, { Role, CreateRoleData } from '../services/roleService';
import Modal from '../components/Modal';
import RoleForm from '../components/RoleForm';
import '../styles/fiis.css';

const RolesPage: React.FC = () => {
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editingRole, setEditingRole] = useState<Role | null>(null);

    useEffect(() => {
        loadRoles();
    }, []);

    const loadRoles = async () => {
        try {
            setLoading(true);
            setError('');
            const data = await roleService.getAll();
            setRoles(data);
        } catch (err: any) {
            console.error('Error loading Roles:', err);
            setError('Failed to load Roles. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = () => {
        setError('');
        setEditingRole(null);
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (role: Role) => {
        setError('');
        setEditingRole(role);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        if (!isSaving) {
            setError('');
            setEditingRole(null);
            setIsModalOpen(false);
        }
    };

    const handleSubmit = async (data: CreateRoleData) => {
        try {
            setIsSaving(true);
            setError('');

            if (editingRole) {
                const updatedRole = await roleService.update(editingRole.pk, data);
                setRoles(roles.map(role => role.pk === updatedRole.pk ? updatedRole : role));
            } else {
                const newRole = await roleService.create(data);
                setRoles([...roles, newRole]);
            }

            setIsModalOpen(false);
        } catch (err: any) {
            console.error(`Error ${editingRole ? 'updating' : 'creating'} Role:`, err);
            setError(err.response?.data?.detail || `Failed to ${editingRole ? 'update' : 'create'} Role. Please try again.`);
            throw err;
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async (pk: number, name: string) => {
        if (!window.confirm(`Are you sure you want to delete ${name}?`)) {
            return;
        }

        try {
            await roleService.delete(pk);
            setRoles(roles.filter(role => role.pk !== pk));
        } catch (err: any) {
            console.error('Error deleting Role:', err);
            setError('Failed to delete Role. Please try again.');
        }
    };

    if (loading) {
        return (
            <div className="fiis-page">
                <div className="loading">Loading Roles...</div>
            </div>
        );
    }

    return (
        <div className="fiis-page">
            <div className="page-header">
                <h1>Roles</h1>
                <button className="btn-primary" onClick={handleOpenModal}>
                    + Add New Role
                </button>
            </div>

            {roles.length === 0 ? (
                <div className="empty-state">
                    <p>No Roles registered yet.</p>
                    <button className="btn-primary" onClick={handleOpenModal}>
                        Add your first Role
                    </button>
                </div>
            ) : (
                <div className="fiis-table-container">
                    <table className="fiis-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Description</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {roles.map(role => (
                                <tr key={role.pk}>
                                    <td className="tag">{role.name}</td>
                                    <td>{role.description || '-'}</td>
                                    <td className="actions">
                                        <button
                                            className="btn-edit"
                                            title="Edit"
                                            onClick={() => handleOpenEditModal(role)}
                                        >
                                            ✏️
                                        </button>
                                        <button
                                            className="btn-delete"
                                            title="Delete"
                                            onClick={() => handleDelete(role.pk, role.name)}
                                        >
                                            🗑️
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            <Modal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                title={editingRole ? 'Edit Role' : 'Add New Role'}
            >
                {error && (
                    <div className="error-message" role="alert">
                        {error}
                    </div>
                )}
                <RoleForm
                    onSubmit={handleSubmit}
                    onCancel={handleCloseModal}
                    isLoading={isSaving}
                    initialData={editingRole ? {
                        name: editingRole.name,
                        description: editingRole.description
                    } : undefined}
                />
            </Modal>
        </div>
    );
};

export default RolesPage;
