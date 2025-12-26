import api from './api';

export interface Transaction {
    pk: number;
    user_pk: number;
    fii_pk: number;
    transaction_type: 'buy' | 'sell';
    transaction_date: string;
    quantity: number;
    price_per_unit: number;
    total_amount: number;
    created_at: string;
    updated_at: string;
}

export interface CreateTransactionData {
    fii_pk: number;
    transaction_type: 'buy' | 'sell';
    transaction_date: string;
    quantity: number;
    price_per_unit: number;
    total_amount: number;
}

export interface UpdateTransactionData {
    fii_pk?: number;
    transaction_type?: 'buy' | 'sell';
    transaction_date?: string;
    quantity?: number;
    price_per_unit?: number;
    total_amount?: number;
}

const transactionService = {
    async getAll(): Promise<Transaction[]> {
        const response = await api.get<Transaction[]>('/transactions');
        return response.data;
    },

    async getById(pk: number): Promise<Transaction> {
        const response = await api.get<Transaction>(`/transactions/${pk}`);
        return response.data;
    },

    async create(data: CreateTransactionData): Promise<Transaction> {
        const response = await api.post<Transaction>('/transactions', data);
        return response.data;
    },

    async update(pk: number, data: UpdateTransactionData): Promise<Transaction> {
        const response = await api.patch<Transaction>(`/transactions/${pk}`, data);
        return response.data;
    },

    async delete(pk: number): Promise<void> {
        await api.delete(`/transactions/${pk}`);
    }
};

export default transactionService;
