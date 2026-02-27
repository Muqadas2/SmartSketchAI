import type { GenerateResult, EditResult } from '../types';

type RightPanelProps = {
  generateResult?: GenerateResult | null;
  editResult?: EditResult | null;
  prompt?: string;
};

function scorePercent(value: number | undefined): number {
  if (value == null || typeof value !== 'number') return 0;
  return Math.round(Math.min(1, Math.max(0, value)) * 100);
}

function RightPanel({ generateResult = null, editResult = null, prompt = '' }: RightPanelProps) {
  const hasGenerate = generateResult != null;
  const hasEdit = editResult != null;
  
  const currentResult = hasEdit ? editResult : generateResult;
  const currentImage = hasEdit ? editResult?.edited_image_url : generateResult?.image_url;
  const scores = currentResult?.scores ?? {};
  
  const clip = scorePercent(scores.clip_score);
  const identity = hasEdit 
    ? scorePercent(editResult?.identity_score) 
    : scorePercent((generateResult?.scores as Record<string, number | undefined>)?.identity_score);
  
  const meta = (currentResult?.metadata ?? {}) as Record<string, unknown>;
  const seed = meta.seed != null ? String(meta.seed) : '—';
  const modelVersion = meta.model_version != null ? String(meta.model_version) : '—';

  const displayPrompt = hasEdit ? editResult?.edit_prompt : prompt;
  const auditId = hasEdit ? editResult?.edit_id : generateResult?.generation_id;

  return (
    <div className="w-80 bg-gray-50 dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 overflow-y-auto">
      <div className="p-4 space-y-6">
        {/* Preview */}
        <div>
          <h2 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
            {hasEdit ? 'Edited Preview' : 'Preview & Workspace'}
          </h2>
          <div className="bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
            <div className="aspect-square bg-gray-100 dark:bg-gray-800 flex items-center justify-center relative">
              {currentImage ? (
                <img
                  src={currentImage}
                  alt={hasEdit ? 'Edited' : 'Generated'}
                  className="w-full h-full object-contain"
                />
              ) : (
                <span className="text-gray-400 dark:text-gray-500 text-sm">Preview</span>
              )}
              <div className="absolute bottom-2 right-2 bg-white/90 dark:bg-gray-900/90 px-2 py-1 rounded text-xs font-medium text-gray-600 dark:text-gray-400">
                RESEARCH USE ONLY
              </div>
            </div>
          </div>
        </div>

        {/* Evaluation Scores */}
        <div>
          <h2 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Evaluation Scores</h2>
          <div className="space-y-3">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">CLIP</span>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">{clip}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${clip >= 80 ? 'bg-green-500' : clip >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${clip}%` }}
                />
              </div>
            </div>
            <div className="bg-white dark:bg-gray-900 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center mb-1">
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                  {hasEdit ? 'Identity Preserved' : 'ArcFace'}
                </span>
                <span className="text-sm font-semibold text-gray-900 dark:text-white">{identity}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${identity >= 80 ? 'bg-green-500' : identity >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                  style={{ width: `${identity}%` }}
                />
              </div>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 mb-1">
              <div className="w-3 h-3 bg-green-500 rounded" />
              <span>0.8-1.0: Excellent</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400 mb-1">
              <div className="w-3 h-3 bg-yellow-500 rounded" />
              <span>0.6-0.8: Good</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
              <div className="w-3 h-3 bg-red-500 rounded" />
              <span>&lt;0.6: Needs Improvement</span>
            </div>
          </div>
        </div>

        {/* Metadata & Audit */}
        <div>
          <h2 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Metadata & Audit</h2>
          <div className="bg-white dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700 space-y-3">
            <div>
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                {hasEdit ? 'Edit Prompt' : 'Prompt'}
              </p>
              <p className="text-xs text-gray-900 dark:text-white">{displayPrompt || '—'}</p>
            </div>
            {hasEdit && (
              <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Original Image</p>
                <p className="text-xs text-gray-900 dark:text-white">#{editResult?.original_image_id}</p>
              </div>
            )}
            <div className="pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-gray-500 dark:text-gray-400">Model:</span>
                <span className="text-gray-900 dark:text-white font-medium">{modelVersion}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500 dark:text-gray-400">Seed:</span>
                <span className="text-gray-900 dark:text-white font-medium">{seed}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500 dark:text-gray-400">
                  {hasEdit ? 'Edit ID' : 'Image ID'}:
                </span>
                <span className="text-gray-900 dark:text-white font-medium">
                  {hasEdit ? `#${editResult?.id}` : hasGenerate ? `#${generateResult?.id}` : '—'}
                </span>
              </div>
            </div>
            <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Audit ID</p>
              <p className="text-xs text-gray-900 dark:text-white font-mono">{auditId ?? '—'}</p>
            </div>
          </div>
          <button
            type="button"
            className="w-full mt-3 bg-gray-900 dark:bg-gray-700 hover:bg-gray-800 dark:hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Export ZIP with Audit Data
          </button>
        </div>
      </div>
    </div>
  );
}

export default RightPanel;
