import React, { useState, useEffect } from 'react';
import roleService, { Role, CreateRoleData } from '../services/roleService';
import permissionService, { Permission } from '../services/permissionService';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import RoleForm from '../components/RoleForm';
import '../styles/fiis.css';

const RolesPage: React.FC = () => {
    const [roles, setRoles] = useState<Role[]>([]);
    const [permissions, setPermissions] = useState<Permission[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editingRole, setEditingRole] = useState<Role | null>(null);
    const [deleteConfirm, setDeleteConfirm] = useState<{ pk: number; name: string } | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        loadRoles();
        loadPermissions();
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

    const loadPermissions = async () => {
        try {
            const data = await permissionService.getAll();
            setPermissions(data);
        } catch (err: any) {
            console.error('Error loading Permissions:', err);
            setError('Failed to load Permissions. Please try again.');
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

    const handleDeleteClick = (pk: number, name: string) => {
        setDeleteConfirm({ pk, name });
    };

    const handleDeleteConfirm = async () => {
        if (!deleteConfirm) return;

        setIsDeleting(true);
        try {
            await roleService.delete(deleteConfirm.pk);
            setRoles(roles.filter(role => role.pk !== deleteConfirm.pk));
            setDeleteConfirm(null);
        } catch (err: any) {
            console.error('Error deleting Role:', err);
            setError('Failed to delete Role. Please try again.');
        } finally {
            setIsDeleting(false);
        }
    };

    const handleDeleteCancel = () => {
        setDeleteConfirm(null);
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
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                            </svg>
                                        </button>
                                        <button
                                            className="btn-delete"
                                            title="Delete"
                                            onClick={() => handleDeleteClick(role.pk, role.name)}
                                        >
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <polyline points="3 6 5 6 21 6"></polyline>
                                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                            </svg>
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
                        description: editingRole.description,
                        permission_pks: editingRole.permission_pks
                    } : undefined}
                    permissions={permissions}
                />
            </Modal>

            {deleteConfirm && (
                <ConfirmDialog
                    isOpen={!!deleteConfirm}
                    onClose={handleDeleteCancel}
                    onConfirm={handleDeleteConfirm}
                    title="Delete Role"
                    message={`Are you sure you want to delete role ${deleteConfirm.name}? This action cannot be undone.`}
                    confirmLabel="Delete"
                    cancelLabel="Cancel"
                    variant="danger"
                    isLoading={isDeleting}
                />
            )}
        </div>
    );
};

export default RolesPage;
