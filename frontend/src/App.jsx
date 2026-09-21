import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import NewApplication from './pages/NewApplication';
import AssessmentResult from './pages/AssessmentResult';
import AdverseActionNotice from './pages/AdverseActionNotice';
import FairnessDashboard from './pages/FairnessDashboard';
import UnderwriterPanel from './pages/UnderwriterPanel';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/apply" element={<NewApplication />} />
        <Route path="/result" element={<AssessmentResult />} />
        <Route path="/notice" element={<AdverseActionNotice />} />
        <Route path="/fairness" element={<FairnessDashboard />} />
        <Route path="/underwriter" element={<UnderwriterPanel />} />
      </Routes>
    </BrowserRouter>
  );
}
