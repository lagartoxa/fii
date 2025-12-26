import api from './api';

export interface FII {
  pk: number;
  tag: string;
  name: string;
  sector?: string;
  cut_day?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateFIIData {
  tag: string;
  name: string;
  sector?: string;
  cut_day?: number;
}

export interface UpdateFIIData {
  tag?: string;
  name?: string;
  sector?: string;
  cut_day?: number;
}

const fiiService = {
  async getAll(): Promise<FII[]> {
    const response = await api.get<FII[]>('/fiis');
    return response.data;
  },

  async getById(pk: number): Promise<FII> {
    const response = await api.get<FII>(`/fiis/${pk}`);
    return response.data;
  },

  async create(data: CreateFIIData): Promise<FII> {
    const response = await api.post<FII>('/fiis', data);
    return response.data;
  },

  async update(pk: number, data: UpdateFIIData): Promise<FII> {
    const response = await api.patch<FII>(`/fiis/${pk}`, data);
    return response.data;
  },

  async delete(pk: number): Promise<void> {
    await api.delete(`/fiis/${pk}`);
  }
};

export default fiiService;
