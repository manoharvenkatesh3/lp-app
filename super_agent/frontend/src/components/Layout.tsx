import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import Logo from "./Logo";
import ThemeToggle from "./ThemeToggle";

const navItems = [
  { to: "/", label: "Overview" },
  { to: "/intake", label: "Intake" },
  { to: "/screening", label: "Screening" },
  { to: "/interviews", label: "Interview Ops" },
  { to: "/insights", label: "Insights" },
  { to: "/integrations", label: "ATS Integrations" }
];

const Layout: React.FC = () => {
  return (
    <div className="app-shell">
      <header className="app-shell__header">
        <div className="app-shell__brand">
          <Logo />
          <div>
            <p className="app-shell__title">Super Agent</p>
            <p className="app-shell__subtitle">Talent Intelligence Command Center</p>
          </div>
        </div>
        <div className="app-shell__actions">
          <ThemeToggle />
          <button className="primary-btn">Launch Workflow</button>
        </div>
      </header>
      <nav className="app-shell__nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `nav-link ${isActive ? "nav-link--active" : ""}`
            }
            end={item.to === "/"}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <main className="app-shell__content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
