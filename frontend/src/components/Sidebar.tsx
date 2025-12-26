import React from 'react';
import { NavLink } from 'react-router-dom';
import '../styles/sidebar.css';

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <ul className="sidebar-menu">
          <li>
            <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
              <span className="icon">🏠</span>
              <span className="label">Home</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/fiis" className={({ isActive }) => isActive ? 'active' : ''}>
              <span className="icon">🏢</span>
              <span className="label">FIIs</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/transactions" className={({ isActive }) => isActive ? 'active' : ''}>
              <span className="icon">💰</span>
              <span className="label">Transactions</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/dividends" className={({ isActive }) => isActive ? 'active' : ''}>
              <span className="icon">💵</span>
              <span className="label">Dividends</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/roles" className={({ isActive }) => isActive ? 'active' : ''}>
              <span className="icon">🎭</span>
              <span className="label">Roles</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/permissions" className={({ isActive }) => isActive ? 'active' : ''}>
              <span className="icon">🔐</span>
              <span className="label">Permissions</span>
            </NavLink>
          </li>
          <li>
            <NavLink to="/users" className={({ isActive }) => isActive ? 'active' : ''}>
              <span className="icon">👤</span>
              <span className="label">Users</span>
            </NavLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
