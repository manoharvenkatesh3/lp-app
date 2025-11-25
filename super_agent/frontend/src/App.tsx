import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import IntakePage from "./pages/IntakePage";
import ScreeningPage from "./pages/ScreeningPage";
import InterviewsPage from "./pages/InterviewsPage";
import InsightsPage from "./pages/InsightsPage";
import IntegrationsPage from "./pages/IntegrationsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="intake" element={<IntakePage />} />
          <Route path="screening" element={<ScreeningPage />} />
          <Route path="interviews" element={<InterviewsPage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="integrations" element={<IntegrationsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
