import React, { useState, useEffect } from 'react';
import userService, { User, CreateUserData } from '../services/userService';
import roleService, { Role } from '../services/roleService';
import Modal from '../components/Modal';
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

    const handleDelete = async (pk: number, username: string) => {
        if (!window.confirm(`Are you sure you want to delete user ${username}?`)) {
            return;
        }

        try {
            await userService.delete(pk);
            setUsers(users.filter(user => user.pk !== pk));
        } catch (err: any) {
            console.error('Error deleting User:', err);
            setError(err.response?.data?.detail || 'Failed to delete User. Please try again.');
        }
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
                                            ✏️
                                        </button>
                                        <button
                                            className="btn-delete"
                                            title="Delete"
                                            onClick={() => handleDelete(user.pk, user.username)}
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
        </div>
    );
};

export default UsersPage;
