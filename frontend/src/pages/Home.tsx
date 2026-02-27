import { useCallback, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/Topbar';
import Workspace from '../components/Workspace';
import RightPanel from '../components/RightPanel';
import type { GenerateResult, EditResult } from '../types';

function Home() {
  const { isAuthenticated } = useAuth();
  const [generateResult, setGenerateResult] = useState<GenerateResult | null>(null);
  const [editResult, setEditResult] = useState<EditResult | null>(null);
  const [currentPrompt, setCurrentPrompt] = useState('');

  const handleGenerateResult = useCallback(
    (result: GenerateResult | null, prompt: string) => {
      setGenerateResult(result);
      setCurrentPrompt(prompt);
      setEditResult(null);
    },
    []
  );

  const handleEditResult = useCallback((result: EditResult | null) => {
    setEditResult(result);
  }, []);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="h-screen flex flex-col bg-white dark:bg-gray-900">
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <Workspace
          onGenerateResult={handleGenerateResult}
          onEditResult={handleEditResult}
        />
        <RightPanel
          generateResult={generateResult}
          editResult={editResult}
          prompt={currentPrompt}
        />
      </div>
    </div>
  );
}

export default Home;
