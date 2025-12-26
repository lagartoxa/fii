import React, { useState, useEffect } from 'react';
import permissionService, { Permission, CreatePermissionData } from '../services/permissionService';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import PermissionForm from '../components/PermissionForm';
import '../styles/fiis.css';

const PermissionsPage: React.FC = () => {
    const [permissions, setPermissions] = useState<Permission[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editingPermission, setEditingPermission] = useState<Permission | null>(null);
    const [deleteConfirm, setDeleteConfirm] = useState<{ pk: number; resource: string; action: string } | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        loadPermissions();
    }, []);

    const loadPermissions = async () => {
        try {
            setLoading(true);
            setError('');
            const data = await permissionService.getAll();
            setPermissions(data);
        } catch (err: any) {
            console.error('Error loading Permissions:', err);
            setError('Failed to load Permissions. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = () => {
        setError('');
        setEditingPermission(null);
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (permission: Permission) => {
        setError('');
        setEditingPermission(permission);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        if (!isSaving) {
            setError('');
            setEditingPermission(null);
            setIsModalOpen(false);
        }
    };

    const handleSubmit = async (data: CreatePermissionData) => {
        try {
            setIsSaving(true);
            setError('');

            if (editingPermission) {
                const updatedPermission = await permissionService.update(editingPermission.pk, data);
                setPermissions(permissions.map(permission => permission.pk === updatedPermission.pk ? updatedPermission : permission));
            } else {
                const newPermission = await permissionService.create(data);
                setPermissions([...permissions, newPermission]);
            }

            setIsModalOpen(false);
        } catch (err: any) {
            console.error(`Error ${editingPermission ? 'updating' : 'creating'} Permission:`, err);
            setError(err.response?.data?.detail || `Failed to ${editingPermission ? 'update' : 'create'} Permission. Please try again.`);
            throw err;
        } finally {
            setIsSaving(false);
        }
    };

    const handleDeleteClick = (pk: number, resource: string, action: string) => {
        setDeleteConfirm({ pk, resource, action });
    };

    const handleDeleteConfirm = async () => {
        if (!deleteConfirm) return;

        setIsDeleting(true);
        try {
            await permissionService.delete(deleteConfirm.pk);
            setPermissions(permissions.filter(permission => permission.pk !== deleteConfirm.pk));
            setDeleteConfirm(null);
        } catch (err: any) {
            console.error('Error deleting Permission:', err);
            setError('Failed to delete Permission. Please try again.');
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
                <div className="loading">Loading Permissions...</div>
            </div>
        );
    }

    return (
        <div className="fiis-page">
            <div className="page-header">
                <h1>Permissions</h1>
                <button className="btn-primary" onClick={handleOpenModal}>
                    + Add New Permission
                </button>
            </div>

            {permissions.length === 0 ? (
                <div className="empty-state">
                    <p>No Permissions registered yet.</p>
                    <button className="btn-primary" onClick={handleOpenModal}>
                        Add your first Permission
                    </button>
                </div>
            ) : (
                <div className="fiis-table-container">
                    <table className="fiis-table">
                        <thead>
                            <tr>
                                <th>Resource</th>
                                <th>Action</th>
                                <th>Description</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {permissions.map(permission => (
                                <tr key={permission.pk}>
                                    <td>{permission.resource}</td>
                                    <td>{permission.action}</td>
                                    <td>{permission.description || '-'}</td>
                                    <td className="actions">
                                        <button
                                            className="btn-edit"
                                            title="Edit"
                                            onClick={() => handleOpenEditModal(permission)}
                                        >
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                            </svg>
                                        </button>
                                        <button
                                            className="btn-delete"
                                            title="Delete"
                                            onClick={() => handleDeleteClick(permission.pk, permission.resource, permission.action)}
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
                title={editingPermission ? 'Edit Permission' : 'Add New Permission'}
            >
                {error && (
                    <div className="error-message" role="alert">
                        {error}
                    </div>
                )}
                <PermissionForm
                    onSubmit={handleSubmit}
                    onCancel={handleCloseModal}
                    isLoading={isSaving}
                    initialData={editingPermission ? {
                        resource: editingPermission.resource,
                        action: editingPermission.action,
                        description: editingPermission.description
                    } : undefined}
                />
            </Modal>

            {deleteConfirm && (
                <ConfirmDialog
                    isOpen={!!deleteConfirm}
                    onClose={handleDeleteCancel}
                    onConfirm={handleDeleteConfirm}
                    title="Delete Permission"
                    message={`Are you sure you want to delete permission ${deleteConfirm.resource}:${deleteConfirm.action}? This action cannot be undone.`}
                    confirmLabel="Delete"
                    cancelLabel="Cancel"
                    variant="danger"
                    isLoading={isDeleting}
                />
            )}
        </div>
    );
};

export default PermissionsPage;
