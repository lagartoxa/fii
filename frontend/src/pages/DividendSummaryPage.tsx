import React, { useState, useEffect } from 'react';
import dividendService, { MonthlySummary } from '../services/dividendService';
import '../styles/fiis.css';

const DividendSummaryPage: React.FC = () => {
    const [summary, setSummary] = useState<MonthlySummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Initialize with current month/year
    const now = new Date();
    const [selectedYear, setSelectedYear] = useState(now.getFullYear());
    const [selectedMonth, setSelectedMonth] = useState(now.getMonth() + 1); // 0-indexed to 1-indexed

    useEffect(() => {
        loadSummary();
    }, [selectedYear, selectedMonth]);

    const loadSummary = async () => {
        try {
            setLoading(true);
            setError('');
            const data = await dividendService.getMonthlySummary(selectedYear, selectedMonth);
            setSummary(data);
        } catch (err: any) {
            console.error('Error loading summary:', err);
            setError('Failed to load dividend summary. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleMonthChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedMonth(parseInt(e.target.value));
    };

    const handleYearChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedYear(parseInt(e.target.value));
    };

    // Generate year options (current year and 5 years back)
    const currentYear = new Date().getFullYear();
    const yearOptions = Array.from({ length: 6 }, (_, i) => currentYear - i);

    const monthNames = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];

    if (loading) {
        return (
            <div className="fiis-page">
                <div className="loading">Loading dividend summary...</div>
            </div>
        );
    }

    return (
        <div className="fiis-page">
            <div className="page-header">
                <h1>Resumo Mensal de Dividendos</h1>
            </div>

            {error && (
                <div className="error-message" role="alert">
                    {error}
                </div>
            )}

            <div className="filters-container" style={{ marginBottom: '20px', display: 'flex', gap: '15px', alignItems: 'center' }}>
                <div>
                    <label htmlFor="month-select" style={{ marginRight: '8px', fontWeight: 600, color: '#ffffff' }}>Mês:</label>
                    <select
                        id="month-select"
                        value={selectedMonth}
                        onChange={handleMonthChange}
                        style={{
                            padding: '8px 12px',
                            borderRadius: '5px',
                            border: '1px solid #3a3a3c',
                            fontSize: '14px',
                            backgroundColor: '#181819',
                            color: '#95989f'
                        }}
                    >
                        {monthNames.map((name, index) => (
                            <option key={index + 1} value={index + 1}>
                                {name}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label htmlFor="year-select" style={{ marginRight: '8px', fontWeight: 600, color: '#ffffff' }}>Ano:</label>
                    <select
                        id="year-select"
                        value={selectedYear}
                        onChange={handleYearChange}
                        style={{
                            padding: '8px 12px',
                            borderRadius: '5px',
                            border: '1px solid #3a3a3c',
                            fontSize: '14px',
                            backgroundColor: '#181819',
                            color: '#95989f'
                        }}
                    >
                        {yearOptions.map(year => (
                            <option key={year} value={year}>
                                {year}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {!summary || summary.fiis.length === 0 ? (
                <div className="empty-state">
                    <p>Nenhum dividendo recebido em {monthNames[selectedMonth - 1]} de {selectedYear}.</p>
                </div>
            ) : (
                <div className="fiis-table-container">
                    <table className="fiis-table">
                        <thead>
                            <tr>
                                <th>FII</th>
                                <th>Data de Pagamento</th>
                                <th>Valor por Cota</th>
                                <th>Cotas Elegíveis</th>
                                <th>Total Recebido</th>
                            </tr>
                        </thead>
                        <tbody>
                            {summary.fiis.map(fii => (
                                <React.Fragment key={fii.fii_pk}>
                                    {fii.dividends.map((dividend, index) => (
                                        <tr key={dividend.dividend_pk}>
                                            {index === 0 && (
                                                <td
                                                    className="tag"
                                                    rowSpan={fii.dividends.length}
                                                    style={{ verticalAlign: 'middle' }}
                                                >
                                                    {fii.fii_tag}
                                                </td>
                                            )}
                                            <td>{dividend.payment_date.split('-').reverse().join('/')}</td>
                                            <td>
                                                R$ {Number(dividend.amount_per_unit).toFixed(4)}
                                            </td>
                                            <td>{dividend.units_held}</td>
                                            <td style={{ fontWeight: 500 }}>
                                                R$ {Number(dividend.total_amount).toFixed(2)}
                                            </td>
                                        </tr>
                                    ))}
                                    {fii.dividends.length > 1 && (
                                        <tr style={{ backgroundColor: '#1f1f20', fontWeight: 600, color: '#ffffff' }}>
                                            <td colSpan={4}>
                                                Subtotal {fii.fii_tag}:
                                            </td>
                                            <td>
                                                R$ {Number(fii.total_amount).toFixed(2)}
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                        </tbody>
                        <tfoot>
                            <tr style={{ fontWeight: 'bold', backgroundColor: '#a2154a', color: '#ffffff' }}>
                                <td colSpan={4}>
                                    Total Geral:
                                </td>
                                <td style={{ fontSize: '16px' }}>
                                    R$ {Number(summary.total).toFixed(2)}
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            )}
        </div>
    );
};

export default DividendSummaryPage;
