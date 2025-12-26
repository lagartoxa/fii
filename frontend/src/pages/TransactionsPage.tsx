import React, { useState, useEffect } from 'react';
import transactionService, { Transaction, CreateTransactionData } from '../services/transactionService';
import fiiService, { FII } from '../services/fiiService';
import Modal from '../components/Modal';
import TransactionForm from '../components/TransactionForm';
import '../styles/fiis.css';

const TransactionsPage: React.FC = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [fiis, setFiis] = useState<FII[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            setError('');
            const [transactionsData, fiisData] = await Promise.all([
                transactionService.getAll(),
                fiiService.getAll()
            ]);
            setTransactions(transactionsData);
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
        setEditingTransaction(null);
        setIsModalOpen(true);
    };

    const handleOpenEditModal = (transaction: Transaction) => {
        setError('');
        setEditingTransaction(transaction);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        if (!isSaving) {
            setError('');
            setEditingTransaction(null);
            setIsModalOpen(false);
        }
    };

    const handleSubmit = async (data: CreateTransactionData) => {
        try {
            setIsSaving(true);
            setError('');

            if (editingTransaction) {
                const updatedTransaction = await transactionService.update(editingTransaction.pk, data);
                setTransactions(transactions.map(t => t.pk === updatedTransaction.pk ? updatedTransaction : t));
            } else {
                const newTransaction = await transactionService.create(data);
                setTransactions([...transactions, newTransaction]);
            }

            setIsModalOpen(false);
        } catch (err: any) {
            console.error(`Error ${editingTransaction ? 'updating' : 'creating'} Transaction:`, err);
            setError(err.response?.data?.detail || `Failed to ${editingTransaction ? 'update' : 'create'} Transaction. Please try again.`);
            throw err;
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async (pk: number) => {
        if (!window.confirm('Are you sure you want to delete this transaction?')) {
            return;
        }

        try {
            await transactionService.delete(pk);
            setTransactions(transactions.filter(t => t.pk !== pk));
        } catch (err: any) {
            console.error('Error deleting Transaction:', err);
            setError('Failed to delete Transaction. Please try again.');
        }
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
                <div className="loading">Loading Transactions...</div>
            </div>
        );
    }

    return (
        <div className="fiis-page">
            <div className="page-header">
                <h1>Transactions</h1>
                <button className="btn-primary" onClick={handleOpenModal}>
                    + Add New Transaction
                </button>
            </div>

            {transactions.length === 0 ? (
                <div className="empty-state">
                    <p>No Transactions registered yet.</p>
                    <button className="btn-primary" onClick={handleOpenModal}>
                        Add your first Transaction
                    </button>
                </div>
            ) : (
                <div className="fiis-table-container">
                    <table className="fiis-table">
                        <thead>
                            <tr>
                                <th>FII</th>
                                <th>Type</th>
                                <th>Date</th>
                                <th>Quantity</th>
                                <th>Price/Unit</th>
                                <th>Total</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {transactions
                                .filter(transaction => fiis.some(fii => fii.pk === transaction.fii_pk))
                                .map(transaction => (
                                    <tr key={transaction.pk}>
                                        <td className="tag">{getFiiTag(transaction.fii_pk)}</td>
                                        <td>
                                            <span className={`badge ${transaction.transaction_type}`}>
                                                {transaction.transaction_type.toUpperCase()}
                                            </span>
                                        </td>
                                        <td>{formatDate(transaction.transaction_date)}</td>
                                        <td>{transaction.quantity}</td>
                                        <td>R$ {Number(transaction.price_per_unit).toFixed(2)}</td>
                                        <td>R$ {Number(transaction.total_amount).toFixed(2)}</td>
                                        <td className="actions">
                                            <button
                                                className="btn-edit"
                                                title="Edit"
                                                onClick={() => handleOpenEditModal(transaction)}
                                            >
                                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                                                </svg>
                                            </button>
                                            <button
                                                className="btn-delete"
                                                title="Delete"
                                                onClick={() => handleDelete(transaction.pk)}
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
                title={editingTransaction ? 'Edit Transaction' : 'Add New Transaction'}
            >
                {error && (
                    <div className="error-message" role="alert">
                        {error}
                    </div>
                )}
                <TransactionForm
                    onSubmit={handleSubmit}
                    onCancel={handleCloseModal}
                    isLoading={isSaving}
                    fiis={fiis}
                    initialData={editingTransaction ? {
                        fii_pk: editingTransaction.fii_pk,
                        transaction_type: editingTransaction.transaction_type,
                        transaction_date: editingTransaction.transaction_date,
                        quantity: editingTransaction.quantity,
                        price_per_unit: editingTransaction.price_per_unit,
                        total_amount: editingTransaction.total_amount
                    } : undefined}
                />
            </Modal>
        </div>
    );
};

export default TransactionsPage;
