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
                    <label htmlFor="month-select" style={{ marginRight: '8px', fontWeight: 500 }}>Mês:</label>
                    <select
                        id="month-select"
                        value={selectedMonth}
                        onChange={handleMonthChange}
                        style={{
                            padding: '8px 12px',
                            borderRadius: '5px',
                            border: '1px solid #dfe6e9',
                            fontSize: '14px'
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
                    <label htmlFor="year-select" style={{ marginRight: '8px', fontWeight: 500 }}>Ano:</label>
                    <select
                        id="year-select"
                        value={selectedYear}
                        onChange={handleYearChange}
                        style={{
                            padding: '8px 12px',
                            borderRadius: '5px',
                            border: '1px solid #dfe6e9',
                            fontSize: '14px'
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
                                <th>Nome</th>
                                <th>Quantidade de Pagamentos</th>
                                <th>Total Recebido</th>
                            </tr>
                        </thead>
                        <tbody>
                            {summary.fiis.map(fii => (
                                <tr key={fii.fii_pk}>
                                    <td className="tag">{fii.fii_tag}</td>
                                    <td>{fii.fii_name}</td>
                                    <td style={{ textAlign: 'center' }}>{fii.dividend_count}</td>
                                    <td style={{ textAlign: 'right', fontWeight: 500 }}>
                                        R$ {Number(fii.total_amount).toFixed(2)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                        <tfoot>
                            <tr style={{ fontWeight: 'bold', backgroundColor: '#f8fafc' }}>
                                <td colSpan={3} style={{ textAlign: 'right', paddingRight: '20px' }}>
                                    Total Geral:
                                </td>
                                <td style={{ textAlign: 'right', fontSize: '16px' }}>
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
