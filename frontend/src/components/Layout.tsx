import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import authService from '../services/authService';
import '../styles/layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleLogout = async () => {
    await authService.logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="layout">
      <Sidebar isCollapsed={sidebarCollapsed} />
      <div className={`main-container ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <header className="main-header">
          <div className="header-left">
            <button onClick={toggleSidebar} className="sidebar-toggle">
              {sidebarCollapsed ? '☰' : '✕'}
            </button>
            <h1 className="app-title">FII Portfolio Manager</h1>
          </div>
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
