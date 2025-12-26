import api from './api';

export interface User {
    pk: number;
    email: string;
    username: string;
    full_name?: string;
    is_active: boolean;
    is_superuser: boolean;
    created_at: string;
    updated_at: string;
}

export interface CreateUserData {
    email: string;
    username: string;
    full_name?: string;
    password: string;
}

export interface UpdateUserData {
    email?: string;
    username?: string;
    full_name?: string;
    password?: string;
    is_active?: boolean;
}

const userService = {
    async getAll(): Promise<User[]> {
        const response = await api.get<User[]>('/users');
        return response.data;
    },

    async getById(pk: number): Promise<User> {
        const response = await api.get<User>(`/users/${pk}`);
        return response.data;
    },

    async create(data: CreateUserData): Promise<User> {
        const response = await api.post<User>('/users', data);
        return response.data;
    },

    async update(pk: number, data: UpdateUserData): Promise<User> {
        const response = await api.patch<User>(`/users/${pk}`, data);
        return response.data;
    },

    async delete(pk: number): Promise<void> {
        await api.delete(`/users/${pk}`);
    }
};

export default userService;
