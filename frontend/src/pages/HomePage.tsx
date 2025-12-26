import React from 'react';
import '../styles/home.css';

const HomePage: React.FC = () => {
  return (
    <div className="home-container">
      <div className="welcome-message">
        <h2>Welcome to FII Portfolio Manager</h2>
        <p>Manage your Brazilian Real Estate Investment Funds portfolio efficiently.</p>
        <div className="dashboard-cards">
          <div className="card">
            <h3>Portfolio Overview</h3>
            <p>View your complete portfolio performance and allocation.</p>
          </div>
          <div className="card">
            <h3>Recent Transactions</h3>
            <p>Track your latest buy and sell operations.</p>
          </div>
          <div className="card">
            <h3>Dividend Calendar</h3>
            <p>Stay updated with upcoming dividend payments.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
