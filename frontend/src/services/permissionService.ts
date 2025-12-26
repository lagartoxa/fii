import api from './api';

export interface Permission {
    pk: number;
    resource: string;
    action: string;
    description?: string;
    created_at: string;
    updated_at: string;
}

export interface CreatePermissionData {
    resource: string;
    action: string;
    description?: string;
}

export interface UpdatePermissionData {
    resource?: string;
    action?: string;
    description?: string;
}

const permissionService = {
    async getAll(): Promise<Permission[]> {
        const response = await api.get<Permission[]>('/permissions');
        return response.data;
    },

    async getById(pk: number): Promise<Permission> {
        const response = await api.get<Permission>(`/permissions/${pk}`);
        return response.data;
    },

    async create(data: CreatePermissionData): Promise<Permission> {
        const response = await api.post<Permission>('/permissions', data);
        return response.data;
    },

    async update(pk: number, data: UpdatePermissionData): Promise<Permission> {
        const response = await api.patch<Permission>(`/permissions/${pk}`, data);
        return response.data;
    },

    async delete(pk: number): Promise<void> {
        await api.delete(`/permissions/${pk}`);
    }
};

export default permissionService;
