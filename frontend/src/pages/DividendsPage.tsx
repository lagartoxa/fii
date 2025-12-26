import React, { useState, useEffect } from 'react';
import dividendService, { Dividend, CreateDividendData } from '../services/dividendService';
import fiiService, { FII } from '../services/fiiService';
import Modal from '../components/Modal';
import ConfirmDialog from '../components/ConfirmDialog';
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
    const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
    const [isDeleting, setIsDeleting] = useState(false);

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

    const handleDeleteClick = (pk: number) => {
        setDeleteConfirm(pk);
    };

    const handleDeleteConfirm = async () => {
        if (!deleteConfirm) return;

        setIsDeleting(true);
        try {
            await dividendService.delete(deleteConfirm);
            setDividends(dividends.filter(d => d.pk !== deleteConfirm));
            setDeleteConfirm(null);
        } catch (err: any) {
            console.error('Error deleting Dividend:', err);
            setError('Failed to delete Dividend. Please try again.');
        } finally {
            setIsDeleting(false);
        }
    };

    const handleDeleteCancel = () => {
        setDeleteConfirm(null);
    };

    const getFiiTag = (fii_pk: number) => {
        const fii = fiis.find(f => f.pk === fii_pk);
        return fii ? fii.tag : 'Unknown';
    };

    const formatDate = (dateString: string): string => {
        // Parse date as YYYY-MM-DD and format as dd/MM/yyyy
        // Avoid timezone issues by parsing components directly
        const [year, month, day] = dateString.split('-');
        return `${day}/${month}/${year}`;
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
                                <th>Data COM</th>
                                <th>Amount/Unit</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {dividends
                                .filter(dividend => fiis.some(fii => fii.pk === dividend.fii_pk))
                                .map(dividend => {
                                    return (
                                        <tr key={dividend.pk}>
                                            <td className="tag">{getFiiTag(dividend.fii_pk)}</td>
                                            <td>{formatDate(dividend.payment_date)}</td>
                                            <td>{dividend.com_date ? formatDate(dividend.com_date) : 'N/A'}</td>
                                            <td>R$ {Number(dividend.amount_per_unit).toFixed(4)}</td>
                                            <td className="actions">
                                            <button
                                                className="btn-edit"
                                                title="Edit"
                                                onClick={() => handleOpenEditModal(dividend)}
                                            >
                                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                                </svg>
                                            </button>
                                            <button
                                                className="btn-delete"
                                                title="Delete"
                                                onClick={() => handleDeleteClick(dividend.pk)}
                                            >
                                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                    <polyline points="3 6 5 6 21 6"></polyline>
                                                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                                </svg>
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
                        amount_per_unit: editingDividend.amount_per_unit,
                        com_date: editingDividend.com_date
                    } : undefined}
                />
            </Modal>

            {deleteConfirm && (
                <ConfirmDialog
                    isOpen={!!deleteConfirm}
                    onClose={handleDeleteCancel}
                    onConfirm={handleDeleteConfirm}
                    title="Delete Dividend"
                    message="Are you sure you want to delete this dividend? This action cannot be undone."
                    confirmLabel="Delete"
                    cancelLabel="Cancel"
                    variant="danger"
                    isLoading={isDeleting}
                />
            )}
        </div>
    );
};

export default DividendsPage;
