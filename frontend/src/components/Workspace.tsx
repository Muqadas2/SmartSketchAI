import { useState, useCallback, useEffect } from 'react';
import { generateForensicSketch, editForensicSketch } from '../lib/api';
import type { GenerateResult, EditResult } from '../types';

type Mode = 'generate' | 'edit';

type WorkspaceProps = {
  onGenerateResult?: (result: GenerateResult | null, prompt: string) => void;
  onEditResult?: (result: EditResult | null) => void;
  selectedImage?: GenerateResult | null;
};

function Workspace({ onGenerateResult, onEditResult, selectedImage }: WorkspaceProps) {
  const [mode, setMode] = useState<Mode>('generate');
  const [prompt, setPrompt] = useState('');
  const [editPrompt, setEditPrompt] = useState('');
  const [strength, setStrength] = useState(0.6);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [lastGenerateResult, setLastGenerateResult] = useState<GenerateResult | null>(null);
  const [lastGeneratePrompt, setLastGeneratePrompt] = useState('');
  const [lastEditResult, setLastEditResult] = useState<EditResult | null>(null);

  // Handle image selection from sidebar (History)
  useEffect(() => {
    if (selectedImage) {
      setLastGenerateResult(selectedImage);
      setLastGeneratePrompt(selectedImage.prompt);
      setLastEditResult(null);
      setMode('edit'); // Automatically switch to Edit mode
    }
  }, [selectedImage]);

  const handleGenerate = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = prompt.trim();
      if (!trimmed) return;

      setError(null);
      setLoading(true);
      try {
        const result = await generateForensicSketch({
          prompt: trimmed,
          case_type: 'criminal',
          age: null,
        });
        setLastGenerateResult(result);
        setLastGeneratePrompt(trimmed);
        setLastEditResult(null);
        onGenerateResult?.(result, trimmed);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Generation failed';
        setError(msg);
        onGenerateResult?.(null, trimmed);
      } finally {
        setLoading(false);
      }
    },
    [prompt, onGenerateResult]
  );

  const handleEdit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = editPrompt.trim();
      if (!trimmed) return;

      if (!lastGenerateResult) {
        setError('Generate an image first before editing');
        return;
      }

      setError(null);
      setLoading(true);
      try {
        const result = await editForensicSketch({
          original_image_id: lastGenerateResult.id,
          edit_prompt: trimmed,
          strength,
        });
        setLastEditResult(result);
        onEditResult?.(result);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Edit failed';
        setError(msg);
        onEditResult?.(null);
      } finally {
        setLoading(false);
      }
    },
    [editPrompt, strength, lastGenerateResult, onEditResult]
  );

  const currentImage = mode === 'edit' && lastEditResult
    ? lastEditResult.edited_image_url
    : lastGenerateResult?.image_url;

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-gray-900 overflow-hidden">
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center py-8">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              Welcome to SmartSketch AI
            </h2>
            <p className="text-gray-600 dark:text-gray-400">AI-powered forensic sketch tool</p>
          </div>

          {/* Mode Toggle */}
          <div className="flex justify-center mb-6">
            <div className="inline-flex rounded-lg border border-gray-300 dark:border-gray-600 p-1 bg-gray-100 dark:bg-gray-800">
              <button
                type="button"
                onClick={() => setMode('generate')}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  mode === 'generate'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Generate
              </button>
              <button
                type="button"
                onClick={() => setMode('edit')}
                disabled={!lastGenerateResult}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  mode === 'edit'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                } ${!lastGenerateResult ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                Edit
              </button>
            </div>
          </div>

          {!lastGenerateResult && mode === 'generate' && (
            <p className="text-center text-sm text-gray-500 dark:text-gray-400 mb-4">
              Generate an image first, then switch to Edit mode to modify it.
            </p>
          )}
        </div>

        {/* Display area */}
        {(lastGeneratePrompt || currentImage) && (
          <div className="max-w-3xl mx-auto space-y-4">
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                  <p className="text-gray-900 dark:text-white">
                    {mode === 'edit' && lastEditResult
                      ? `Edit: ${lastEditResult.edit_prompt}`
                      : lastGeneratePrompt}
                  </p>
                </div>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  AI Assistant {mode === 'edit' && lastEditResult ? '(Edited)' : ''}
                </span>
                <div className="mt-2 bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                  {currentImage ? (
                    <img
                      src={currentImage}
                      alt={mode === 'edit' ? 'Edited' : 'Generated'}
                      className="max-w-full h-auto rounded-lg border border-gray-200 dark:border-gray-700"
                    />
                  ) : (
                    <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg h-64 flex items-center justify-center bg-white dark:bg-gray-900">
                      <span className="text-gray-500 dark:text-gray-400 text-sm">
                        {loading ? 'Processing…' : 'No image yet'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Show original vs edited in edit mode */}
            {mode === 'edit' && lastEditResult && lastGenerateResult && (
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">Original</p>
                  <img
                    src={lastGenerateResult.image_url}
                    alt="Original"
                    className="w-full rounded-lg border border-gray-200 dark:border-gray-700"
                  />
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
                    Edited (Identity: {(lastEditResult.identity_score * 100).toFixed(0)}%)
                  </p>
                  <img
                    src={lastEditResult.edited_image_url}
                    alt="Edited"
                    className="w-full rounded-lg border border-gray-200 dark:border-gray-700"
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="max-w-3xl mx-auto">
            <p className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg" role="alert">
              {error}
            </p>
          </div>
        )}
      </div>

      {/* Input Area */}
      {mode === 'generate' ? (
        <form onSubmit={handleGenerate} className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
          <div className="max-w-3xl mx-auto flex gap-2">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the person (e.g., young man with glasses and short hair)"
              className="flex-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 dark:focus:ring-gray-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !prompt.trim()}
              className="bg-gray-900 dark:bg-gray-700 hover:bg-gray-800 dark:hover:bg-gray-600 disabled:opacity-50 text-white px-4 py-3 rounded-lg text-sm font-medium transition-colors"
            >
              {loading ? 'Generating…' : 'Generate'}
            </button>
          </div>
        </form>
      ) : (
        <form onSubmit={handleEdit} className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
          <div className="max-w-3xl mx-auto space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={editPrompt}
                onChange={(e) => setEditPrompt(e.target.value)}
                placeholder="Describe the edit (e.g., add glasses, add beard, make older)"
                className="flex-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 dark:focus:ring-gray-500 focus:border-transparent"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !editPrompt.trim() || !lastGenerateResult}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-3 rounded-lg text-sm font-medium transition-colors"
              >
                {loading ? 'Editing…' : 'Edit'}
              </button>
            </div>
            <div className="flex items-center gap-3">
              <label className="text-xs text-gray-600 dark:text-gray-400">Strength:</label>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={strength}
                onChange={(e) => setStrength(parseFloat(e.target.value))}
                className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
              <span className="text-xs text-gray-600 dark:text-gray-400 w-8">{strength.toFixed(1)}</span>
            </div>
          </div>
        </form>
      )}
    </div>
  );
}

export default Workspace;
