import React, { useState, useEffect } from 'react';
import dividendService, { Dividend, CreateDividendData } from '../services/dividendService';
import fiiService, { FII } from '../services/fiiService';
import Modal from '../components/Modal';
import DividendForm from '../components/DividendForm';
import '../styles/fiis.css';

const DividendsPage: React.FC = () => {
    const [dividends, setDividends] = useState<Dividend[]>([]);
    const [fiis, setFiis] = useState<FII[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editingDividend, setEditingDividend] = useState<Dividend | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            setError('');
            const [dividendsData, fiisData] = await Promise.all([
                dividendService.getAll(),
                fiiService.getAll()
            ]);
            setDividends(dividendsData);
            setFiis(fiisData);
        } catch (err: any) {
            console.error('Error loading data:', err);
            setError('Failed to load data. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = () => {
        setError('');
        setEditingDividend(null);
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (dividend: Dividend) => {
        setError('');
        setEditingDividend(dividend);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        if (!isSaving) {
            setError('');
            setEditingDividend(null);
            setIsModalOpen(false);
        }
    };

    const handleSubmit = async (data: CreateDividendData) => {
        try {
            setIsSaving(true);
            setError('');

            if (editingDividend) {
                const updatedDividend = await dividendService.update(editingDividend.pk, data);
                setDividends(dividends.map(d => d.pk === updatedDividend.pk ? updatedDividend : d));
            } else {
                const newDividend = await dividendService.create(data);
                setDividends([...dividends, newDividend]);
            }

            setIsModalOpen(false);
        } catch (err: any) {
            console.error(`Error ${editingDividend ? 'updating' : 'creating'} Dividend:`, err);
            setError(err.response?.data?.detail || `Failed to ${editingDividend ? 'update' : 'create'} Dividend. Please try again.`);
            throw err;
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async (pk: number) => {
        if (!window.confirm('Are you sure you want to delete this dividend?')) {
            return;
        }

        try {
            await dividendService.delete(pk);
            setDividends(dividends.filter(d => d.pk !== pk));
        } catch (err: any) {
            console.error('Error deleting Dividend:', err);
            setError('Failed to delete Dividend. Please try again.');
        }
    };

    const getFiiTag = (fii_pk: number) => {
        const fii = fiis.find(f => f.pk === fii_pk);
        return fii ? fii.tag : 'Unknown';
    };

    const getFiiCutDay = (fii_pk: number): number | undefined => {
        const fii = fiis.find(f => f.pk === fii_pk);
        return fii?.cut_day;
    };

    const formatDate = (dateString: string): string => {
        // Parse date as YYYY-MM-DD and format as dd/MM/yyyy
        // Avoid timezone issues by parsing components directly
        const [year, month, day] = dateString.split('-');
        return `${day}/${month}/${year}`;
    };

    const calculateCutDate = (paymentDate: string, cutDay: number | undefined): string => {
        if (!cutDay) return 'N/A';

        const payment = new Date(paymentDate);
        const year = payment.getFullYear();
        const month = payment.getMonth(); // 0-indexed

        // Cut date is in the same month as payment date
        // Handle months with fewer days
        const lastDayOfMonth = new Date(year, month + 1, 0).getDate();
        const actualDay = Math.min(cutDay, lastDayOfMonth);

        const cutDate = new Date(year, month, actualDay);
        return cutDate.toLocaleDateString('pt-BR');
    };

    if (loading) {
        return (
            <div className="fiis-page">
                <div className="loading">Loading Dividends...</div>
            </div>
        );
    }

    return (
        <div className="fiis-page">
            <div className="page-header">
                <h1>Dividends</h1>
                <button className="btn-primary" onClick={handleOpenModal}>
                    + Add New Dividend
                </button>
            </div>

            {dividends.length === 0 ? (
                <div className="empty-state">
                    <p>No Dividends registered yet.</p>
                    <button className="btn-primary" onClick={handleOpenModal}>
                        Add your first Dividend
                    </button>
                </div>
            ) : (
                <div className="fiis-table-container">
                    <table className="fiis-table">
                        <thead>
                            <tr>
                                <th>FII</th>
                                <th>Payment Date</th>
                                <th>Cut Date</th>
                                <th>Amount/Unit</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dividends
                                .filter(dividend => fiis.some(fii => fii.pk === dividend.fii_pk))
                                .map(dividend => {
                                    const cutDay = getFiiCutDay(dividend.fii_pk);
                                    const cutDate = calculateCutDate(dividend.payment_date, cutDay);

                                    return (
                                        <tr key={dividend.pk}>
                                            <td className="tag">{getFiiTag(dividend.fii_pk)}</td>
                                            <td>{formatDate(dividend.payment_date)}</td>
                                            <td>{cutDate}</td>
                                            <td>R$ {Number(dividend.amount_per_unit).toFixed(4)}</td>
                                            <td className="actions">
                                            <button
                                                className="btn-edit"
                                                title="Edit"
                                                onClick={() => handleOpenEditModal(dividend)}
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                className="btn-delete"
                                                title="Delete"
                                                onClick={() => handleDelete(dividend.pk)}
                                            >
                                                🗑️
                                            </button>
                                        </td>
                                    </tr>
                                    );
                                })}
                        </tbody>
                    </table>
                </div>
            )}

            <Modal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                title={editingDividend ? 'Edit Dividend' : 'Add New Dividend'}
            >
                {error && (
                    <div className="error-message" role="alert">
                        {error}
                    </div>
                )}
                <DividendForm
                    onSubmit={handleSubmit}
                    onCancel={handleCloseModal}
                    isLoading={isSaving}
                    fiis={fiis}
                    initialData={editingDividend ? {
                        fii_pk: editingDividend.fii_pk,
                        payment_date: editingDividend.payment_date,
                        amount_per_unit: editingDividend.amount_per_unit
                    } : undefined}
                />
            </Modal>
        </div>
    );
};

export default DividendsPage;
