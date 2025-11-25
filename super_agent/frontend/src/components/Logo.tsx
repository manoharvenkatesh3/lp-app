import React from "react";

const Logo: React.FC = () => {
  return (
    <svg width="40" height="40" viewBox="0 0 100 100" className="logo">
      <circle cx="50" cy="50" r="45" fill="var(--primary-color)" />
      <text
        x="50"
        y="70"
        textAnchor="middle"
        fontSize="64"
        fontFamily="sans-serif"
        fill="#fff"
        fontWeight="bold"
      >
        S
      </text>
    </svg>
  );
};

export default Logo;
