import api from './api';

export interface Role {
    pk: number;
    name: string;
    description?: string;
    created_at: string;
    updated_at: string;
}

export interface CreateRoleData {
    name: string;
    description?: string;
}

export interface UpdateRoleData {
    name?: string;
    description?: string;
}

const roleService = {
    async getAll(): Promise<Role[]> {
        const response = await api.get<Role[]>('/roles');
        return response.data;
    },

    async getById(pk: number): Promise<Role> {
        const response = await api.get<Role>(`/roles/${pk}`);
        return response.data;
    },

    async create(data: CreateRoleData): Promise<Role> {
        const response = await api.post<Role>('/roles', data);
        return response.data;
    },

    async update(pk: number, data: UpdateRoleData): Promise<Role> {
        const response = await api.patch<Role>(`/roles/${pk}`, data);
        return response.data;
    },

    async delete(pk: number): Promise<void> {
        await api.delete(`/roles/${pk}`);
    }
};

export default roleService;
