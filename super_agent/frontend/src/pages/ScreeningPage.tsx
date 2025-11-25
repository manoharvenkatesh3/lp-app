import React from "react";

const ScreeningPage: React.FC = () => {
  return (
    <div className="page-container">
      <h2>Screening & Ranking</h2>
      <p>AI-powered resume parsing and candidate scoring.</p>
      <div className="card">
        <h3>Top Matches</h3>
        <p>No candidates matched yet. Upload resumes to get started.</p>
      </div>
    </div>
  );
};

export default ScreeningPage;
