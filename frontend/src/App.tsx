import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Settings from './pages/Settings';
import PrivacyPolicy from './pages/PrivacyPolicy';
import Feedback from './pages/Feedback';
import TermsOfService from './pages/TermsOfService';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/settings/privacy" element={<PrivacyPolicy />} />
        <Route path="/settings/feedback" element={<Feedback />} />
        <Route path="/settings/terms" element={<TermsOfService />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
