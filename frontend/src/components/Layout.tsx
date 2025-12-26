import React from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import authService from '../services/authService';
import '../styles/layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <Sidebar />
      <div className="main-container">
        <header className="main-header">
          <h1 className="app-title">FII Portfolio Manager</h1>
          <button onClick={handleLogout} className="logout-button">
            Logout
          </button>
        </header>
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
