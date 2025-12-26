import React, { useState, FormEvent, useEffect } from 'react';
import { CreateFIIData } from '../services/fiiService';
import '../styles/fii-form.css';

interface FIIFormProps {
  onSubmit: (data: CreateFIIData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  initialData?: CreateFIIData;
}

const FIIForm: React.FC<FIIFormProps> = ({
  onSubmit,
  onCancel,
  isLoading = false,
  initialData
}) => {
  const [formData, setFormData] = useState<CreateFIIData>({
    tag: '',
    name: '',
    sector: '',
    cut_day: undefined
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.tag.trim()) {
      newErrors.tag = 'Tag is required';
    } else if (!/^[A-Z]{4}[0-9]{1,2}$/.test(formData.tag.toUpperCase())) {
      newErrors.tag = 'Tag must be in format: ABCD11';
    }

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const dataToSubmit: CreateFIIData = {
      tag: formData.tag.toUpperCase(),
      name: formData.name,
      sector: formData.sector || undefined,
      cut_day: formData.cut_day || undefined
    };

    await onSubmit(dataToSubmit);
  };

  const handleChange = (field: keyof CreateFIIData, value: string | number | undefined) => {
    setFormData({ ...formData, [field]: value });
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="fii-form">
      <div className="form-group">
        <label htmlFor="tag">
          Tag <span className="required">*</span>
        </label>
        <input
          type="text"
          id="tag"
          value={formData.tag}
          onChange={(e) => handleChange('tag', e.target.value.toUpperCase())}
          disabled={isLoading}
          placeholder="e.g., HGLG11"
          maxLength={20}
          className={errors.tag ? 'error' : ''}
        />
        {errors.tag && <span className="error-text">{errors.tag}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="name">
          Name <span className="required">*</span>
        </label>
        <input
          type="text"
          id="name"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          disabled={isLoading}
          placeholder="Full name of the FII"
          maxLength={255}
          className={errors.name ? 'error' : ''}
        />
        {errors.name && <span className="error-text">{errors.name}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="sector">Sector</label>
        <select
          id="sector"
          value={formData.sector}
          onChange={(e) => handleChange('sector', e.target.value)}
          disabled={isLoading}
        >
          <option value="">Select sector</option>
          <option value="Logística">Logística</option>
          <option value="Lajes Corporativas">Lajes Corporativas</option>
          <option value="Shopping">Shopping</option>
          <option value="Híbrido">Híbrido</option>
          <option value="Recebíveis">Recebíveis</option>
          <option value="Papel">Papel</option>
          <option value="Agências">Agências</option>
          <option value="Hospital">Hospital</option>
          <option value="Educacional">Educacional</option>
          <option value="Hotel">Hotel</option>
          <option value="Residencial">Residencial</option>
          <option value="Comercial">Comercial</option>
          <option value="Outros">Outros</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="cut_day">Cut Day</label>
        <input
          type="number"
          id="cut_day"
          value={formData.cut_day || ''}
          onChange={(e) => {
            const value = e.target.value;
            handleChange('cut_day', value === '' ? undefined : parseInt(value));
          }}
          disabled={isLoading}
          placeholder="1-31"
          min={1}
          max={31}
        />
        <span className="help-text">Day of month for dividend cut-off (1-31). Units held will be calculated automatically based on transactions up to this day each month.</span>
      </div>

      <div className="form-actions">
        <button
          type="button"
          onClick={onCancel}
          className="btn-secondary"
          disabled={isLoading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  );
};

export default FIIForm;
