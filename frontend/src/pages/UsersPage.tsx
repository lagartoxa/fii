import React, { useState, useEffect } from 'react';
import userService, { User, CreateUserData } from '../services/userService';
import roleService, { Role } from '../services/roleService';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
import UserForm from '../components/UserForm';
import '../styles/fiis.css';

const UsersPage: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editingUser, setEditingUser] = useState<User | null>(null);
    const [deleteConfirm, setDeleteConfirm] = useState<{ pk: number; username: string } | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);

    useEffect(() => {
        loadUsers();
        loadRoles();
    }, []);

    const loadUsers = async () => {
        try {
            setLoading(true);
            setError('');
            const data = await userService.getAll();
            setUsers(data);
        } catch (err: any) {
            console.error('Error loading Users:', err);
            setError('Failed to load Users. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const loadRoles = async () => {
        try {
            const data = await roleService.getAll();
            setRoles(data);
        } catch (err: any) {
            console.error('Error loading Roles:', err);
            setError('Failed to load Roles. Please try again.');
        }
    };

    const handleOpenModal = () => {
        setError('');
        setEditingUser(null);
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (user: User) => {
        setError('');
        setEditingUser(user);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        if (!isSaving) {
            setError('');
            setEditingUser(null);
            setIsModalOpen(false);
        }
    };

    const handleSubmit = async (data: CreateUserData) => {
        try {
            setIsSaving(true);
            setError('');

            if (editingUser) {
                const updateData: any = { ...data };
                // Remove password if empty
                if (!updateData.password) {
                    delete updateData.password;
                }
                const updatedUser = await userService.update(editingUser.pk, updateData);
                setUsers(users.map(user => user.pk === updatedUser.pk ? updatedUser : user));
            } else {
                const newUser = await userService.create(data);
                setUsers([...users, newUser]);
            }

            setIsModalOpen(false);
        } catch (err: any) {
            console.error(`Error ${editingUser ? 'updating' : 'creating'} User:`, err);
            setError(err.response?.data?.detail || `Failed to ${editingUser ? 'update' : 'create'} User. Please try again.`);
            throw err;
        } finally {
            setIsSaving(false);
        }
    };

    const handleToggleActive = async (user: User) => {
        try {
            const updatedUser = await userService.update(user.pk, {
                is_active: !user.is_active
            });
            setUsers(users.map(u => u.pk === updatedUser.pk ? updatedUser : u));
        } catch (err: any) {
            console.error('Error toggling user status:', err);
            setError(err.response?.data?.detail || 'Failed to update user status. Please try again.');
        }
    };

    const handleDeleteClick = (pk: number, username: string) => {
        setDeleteConfirm({ pk, username });
    };

    const handleDeleteConfirm = async () => {
        if (!deleteConfirm) return;

        setIsDeleting(true);
        try {
            await userService.delete(deleteConfirm.pk);
            setUsers(users.filter(user => user.pk !== deleteConfirm.pk));
            setDeleteConfirm(null);
        } catch (err: any) {
            console.error('Error deleting User:', err);
            setError(err.response?.data?.detail || 'Failed to delete User. Please try again.');
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
                <div className="loading">Loading Users...</div>
            </div>
        );
    }

    return (
        <div className="fiis-page">
            <div className="page-header">
                <h1>Users</h1>
                <button className="btn-primary" onClick={handleOpenModal}>
                    + Add New User
                </button>
            </div>

            {error && !isModalOpen && (
                <div className="error-message" role="alert">
                    {error}
                </div>
            )}

            {users.length === 0 ? (
                <div className="empty-state">
                    <p>No Users registered yet.</p>
                    <button className="btn-primary" onClick={handleOpenModal}>
                        Add your first User
                    </button>
                </div>
            ) : (
                <div className="fiis-table-container">
                    <table className="fiis-table">
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Full Name</th>
                                <th>Status</th>
                                <th>Superuser</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.pk}>
                                    <td className="tag">{user.username}</td>
                                    <td>{user.email}</td>
                                    <td>{user.full_name || '-'}</td>
                                    <td>
                                        <label className="switch">
                                            <input
                                                type="checkbox"
                                                checked={user.is_active}
                                                onChange={() => handleToggleActive(user)}
                                            />
                                            <span className="slider"></span>
                                        </label>
                                    </td>
                                    <td>{user.is_superuser ? '✓' : '-'}</td>
                                    <td className="actions">
                                        <button
                                            className="btn-edit"
                                            title="Edit"
                                            onClick={() => handleOpenEditModal(user)}
                                        >
                                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                            </svg>
                                        </button>
                                        <button
                                            className="btn-delete"
                                            title="Delete"
                                            onClick={() => handleDeleteClick(user.pk, user.username)}
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
                title={editingUser ? 'Edit User' : 'Add New User'}
            >
                {error && (
                    <div className="error-message" role="alert">
                        {error}
                    </div>
                )}
                <UserForm
                    onSubmit={handleSubmit}
                    onCancel={handleCloseModal}
                    isLoading={isSaving}
                    initialData={editingUser ? {
                        email: editingUser.email,
                        username: editingUser.username,
                        full_name: editingUser.full_name,
                        password: '', // Always empty for security
                        is_active: editingUser.is_active,
                        role_pks: editingUser.role_pks
                    } : undefined}
                    isEditMode={!!editingUser}
                    roles={roles}
                />
            </Modal>

            {deleteConfirm && (
                <ConfirmDialog
                    isOpen={!!deleteConfirm}
                    onClose={handleDeleteCancel}
                    onConfirm={handleDeleteConfirm}
                    title="Delete User"
                    message={`Are you sure you want to delete user ${deleteConfirm.username}? This action cannot be undone.`}
                    confirmLabel="Delete"
                    cancelLabel="Cancel"
                    variant="danger"
                    isLoading={isDeleting}
                />
            )}
        </div>
    );
};

export default UsersPage;
