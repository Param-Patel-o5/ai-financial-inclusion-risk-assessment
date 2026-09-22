import { BrowserRouter, Routes, Route } from 'react-router-dom';
import StatusBar from './components/StatusBar';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import NewApplication from './pages/NewApplication';
import DataDictionary from './pages/DataDictionary';
import AssessmentResult from './pages/AssessmentResult';
import AdverseActionNotice from './pages/AdverseActionNotice';
import FairnessDashboard from './pages/FairnessDashboard';
import UnderwriterPanel from './pages/UnderwriterPanel';

export default function App() {
  return (
    <BrowserRouter>
      <StatusBar />
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/apply" element={<NewApplication />} />
        <Route path="/dictionary" element={<DataDictionary />} />
        <Route path="/result" element={<AssessmentResult />} />
        <Route path="/notice" element={<AdverseActionNotice />} />
        <Route path="/fairness" element={<FairnessDashboard />} />
        <Route path="/underwriter" element={<UnderwriterPanel />} />
      </Routes>
    </BrowserRouter>
  );
}
