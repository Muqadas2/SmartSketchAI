import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Settings from './pages/Settings';
import PrivacyPolicy from './pages/PrivacyPolicy';
import Feedback from './pages/Feedback';
import TermsOfService from './pages/TermsOfService';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/settings/privacy" element={<PrivacyPolicy />} />
        <Route path="/settings/feedback" element={<Feedback />} />
        <Route path="/settings/terms" element={<TermsOfService />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
