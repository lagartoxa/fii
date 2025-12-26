import React, { useState, useEffect } from 'react';
import fiiService, { FII, CreateFIIData } from '../services/fiiService';
import Modal from '../components/Modal';
import FIIForm from '../components/FIIForm';
import '../styles/fiis.css';

const FIIsPage: React.FC = () => {
  const [fiis, setFiis] = useState<FII[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editingFii, setEditingFii] = useState<FII | null>(null);

  useEffect(() => {
    loadFiis();
  }, []);

  const loadFiis = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await fiiService.getAll();
      setFiis(data);
    } catch (err: any) {
      console.error('Error loading FIIs:', err);
      setError('Failed to load FIIs. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = () => {
    setError('');  // Clear error when opening modal
    setEditingFii(null);  // Clear editing state
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (fii: FII) => {
    setError('');  // Clear error when opening modal
    setEditingFii(fii);  // Set the FII to edit
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    if (!isSaving) {
      setError('');  // Clear error when closing modal
      setEditingFii(null);  // Clear editing state
      setIsModalOpen(false);
    }
  };

  const handleSubmit = async (data: CreateFIIData) => {
    try {
      setIsSaving(true);
      setError('');

      if (editingFii) {
        // Update existing FII
        const updatedFii = await fiiService.update(editingFii.pk, data);
        setFiis(fiis.map(fii => fii.pk === updatedFii.pk ? updatedFii : fii));
      } else {
        // Create new FII
        const newFii = await fiiService.create(data);
        setFiis([...fiis, newFii]);
      }

      setIsModalOpen(false);
    } catch (err: any) {
      console.error(`Error ${editingFii ? 'updating' : 'creating'} FII:`, err);
      setError(err.response?.data?.detail || `Failed to ${editingFii ? 'update' : 'create'} FII. Please try again.`);
      throw err;
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (pk: number, tag: string) => {
    if (!window.confirm(`Are you sure you want to delete ${tag}?`)) {
      return;
    }

    try {
      await fiiService.delete(pk);
      setFiis(fiis.filter(fii => fii.pk !== pk));
    } catch (err: any) {
      console.error('Error deleting FII:', err);
      setError('Failed to delete FII. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="fiis-page">
        <div className="loading">Loading FIIs...</div>
      </div>
    );
  }

  return (
    <div className="fiis-page">
      <div className="page-header">
        <h1>Fundos Imobiliários</h1>
        <button className="btn-primary" onClick={handleOpenModal}>
          + Add New FII
        </button>
      </div>

      {fiis.length === 0 ? (
        <div className="empty-state">
          <p>No FIIs registered yet.</p>
          <button className="btn-primary" onClick={handleOpenModal}>
            Add your first FII
          </button>
        </div>
      ) : (
        <div className="fiis-table-container">
          <table className="fiis-table">
            <thead>
              <tr>
                <th>Tag</th>
                <th>Name</th>
                <th>Sector</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {fiis.map(fii => (
                <tr key={fii.pk}>
                  <td className="tag">{fii.tag}</td>
                  <td>{fii.name}</td>
                  <td>{fii.sector || '-'}</td>
                  <td className="actions">
                    <button
                      className="btn-edit"
                      title="Edit"
                      onClick={() => handleOpenEditModal(fii)}
                    >
                      ✏️
                    </button>
                    <button
                      className="btn-delete"
                      title="Delete"
                      onClick={() => handleDelete(fii.pk, fii.tag)}
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
        title={editingFii ? 'Edit FII' : 'Add New FII'}
      >
        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}
        <FIIForm
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isLoading={isSaving}
          initialData={editingFii ? {
            tag: editingFii.tag,
            name: editingFii.name,
            sector: editingFii.sector
          } : undefined}
        />
      </Modal>
    </div>
  );
};

export default FIIsPage;
