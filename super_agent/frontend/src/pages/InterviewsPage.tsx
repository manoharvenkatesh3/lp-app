import React from "react";

const InterviewsPage: React.FC = () => {
  return (
    <div className="page-container">
      <h2>Interview Operations</h2>
      <p>Coordinate schedules, capture transcripts, and manage scorecards.</p>
      <div className="card">
        <h3>Upcoming Interviews</h3>
        <ul>
          <li>No interviews scheduled. Sync calendars to populate.</li>
        </ul>
      </div>
    </div>
  );
};

export default InterviewsPage;
