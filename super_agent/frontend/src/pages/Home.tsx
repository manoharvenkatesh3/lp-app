import React from "react";

const Home: React.FC = () => {
  return (
    <div className="page-container">
      <section className="hero-section">
        <h1 className="hero-title">Welcome to Super Agent</h1>
        <p className="hero-subtitle">
          Your AI-powered talent intelligence platform
        </p>
        <div className="card-grid">
          <div className="stat-card">
            <span className="stat-label">Active Candidates</span>
            <span className="stat-value">247</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Interviews Scheduled</span>
            <span className="stat-value">42</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Offers Extended</span>
            <span className="stat-value">18</span>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
