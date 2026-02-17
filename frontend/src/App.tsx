import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LivePage from "./pages/LivePage";
import ReplayPage from "./pages/ReplayPage";
import DriverAnalyticsPage from "./pages/DriverAnalyticsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/live" />} />
        <Route path="/live" element={<LivePage />} />
        <Route path="/replay" element={<ReplayPage />} />
        <Route path="/driver-analytics" element={<DriverAnalyticsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;