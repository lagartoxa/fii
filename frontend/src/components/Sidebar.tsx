import React from 'react';
import { NavLink } from 'react-router-dom';
import '../styles/sidebar.css';

interface SidebarProps {
  isCollapsed: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed }) => {
  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <NavLink to="/" className="sidebar-logo">
        <img
          src={isCollapsed ? "/lagartoxa-logo.png" : "/lagartoxa-full.png"}
          alt="Logo"
        />
      </NavLink>

      <nav className="sidebar-nav">
        <ul className="sidebar-menu">
          <li>
            <NavLink
              to="/"
              className={({ isActive }) => isActive ? 'active' : ''}
              title="Home"
            >
              <span className="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                  <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
              </span>
              <span className="label">Home</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/fiis"
              className={({ isActive }) => isActive ? 'active' : ''}
              title="FIIs"
            >
              <span className="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                </svg>
              </span>
              <span className="label">FIIs</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/transactions"
              className={({ isActive }) => isActive ? 'active' : ''}
              title="Transactions"
            >
              <span className="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="1" x2="12" y2="23"></line>
                  <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
              </span>
              <span className="label">Transactions</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/dividends"
              end
              className={({ isActive }) => isActive ? 'active' : ''}
              title="Dividends"
            >
              <span className="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <polyline points="19 12 12 19 5 12"></polyline>
                </svg>
              </span>
              <span className="label">Dividends</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/dividends/summary"
              className={({ isActive }) => isActive ? 'active' : ''}
              title="Monthly Summary"
            >
              <span className="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
              </span>
              <span className="label">Monthly Summary</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/users"
              className={({ isActive }) => isActive ? 'active' : ''}
              title="Users"
            >
              <span className="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
              </span>
              <span className="label">Users</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/roles"
              className={({ isActive }) => isActive ? 'active' : ''}
              title="Roles"
            >
              <span className="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3"></circle>
                  <path d="M12 1v6m0 6v6"></path>
                  <path d="m4.2 4.2 4.2 4.2m5.6 5.6 4.2 4.2"></path>
                  <path d="M1 12h6m6 0h6"></path>
                  <path d="m4.2 19.8 4.2-4.2m5.6-5.6 4.2-4.2"></path>
                </svg>
              </span>
              <span className="label">Roles</span>
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/permissions"
              className={({ isActive }) => isActive ? 'active' : ''}
              title="Permissions"
            >
              <span className="icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </span>
              <span className="label">Permissions</span>
            </NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
