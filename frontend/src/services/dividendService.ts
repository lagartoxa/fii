import api from './api';

export interface Dividend {
    pk: number;
    user_pk: number;
    fii_pk: number;
    payment_date: string;
    reference_date?: string;
    amount_per_unit: number;
    units_held: number;
    total_amount: number;
    created_at: string;
    updated_at: string;
}

export interface CreateDividendData {
    fii_pk: number;
    payment_date: string;
    reference_date?: string;
    amount_per_unit: number;
    units_held: number;
    total_amount: number;
}

export interface UpdateDividendData {
    fii_pk?: number;
    payment_date?: string;
    reference_date?: string;
    amount_per_unit?: number;
    units_held?: number;
    total_amount?: number;
}

const dividendService = {
    async getAll(): Promise<Dividend[]> {
        const response = await api.get<Dividend[]>('/dividends');
        return response.data;
    },

    async getById(pk: number): Promise<Dividend> {
        const response = await api.get<Dividend>(`/dividends/${pk}`);
        return response.data;
    },

    async create(data: CreateDividendData): Promise<Dividend> {
        const response = await api.post<Dividend>('/dividends', data);
        return response.data;
    },

    async update(pk: number, data: UpdateDividendData): Promise<Dividend> {
        const response = await api.patch<Dividend>(`/dividends/${pk}`, data);
        return response.data;
    },

    async delete(pk: number): Promise<void> {
        await api.delete(`/dividends/${pk}`);
    }
};

export default dividendService;
