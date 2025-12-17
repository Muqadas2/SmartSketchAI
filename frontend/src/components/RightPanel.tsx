function RightPanel() {
    return (
      <div className="w-80 bg-gray-50 border-l border-gray-200 overflow-y-auto">
        <div className="p-4 space-y-6">
          {/* Preview & Workspace */}
          <div>
            <h2 className="text-sm font-semibold text-gray-900 mb-3">Preview & Workspace</h2>
            <div className="bg-white border border-gray-300 rounded-lg overflow-hidden">
              <div className="aspect-square bg-gray-100 flex items-center justify-center relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-gray-400 text-sm">Futuristic Cityscape Preview</span>
                </div>
                <div className="absolute bottom-2 right-2 bg-white/90 px-2 py-1 rounded text-xs font-medium text-gray-600">
                  RESEARCH USE ONLY
                </div>
              </div>
            </div>
          </div>

          {/* Evaluation Scores */}
          <div>
            <h2 className="text-sm font-semibold text-gray-900 mb-3">Evaluation Scores</h2>
            <div className="space-y-3">
              <div className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-medium text-gray-700">CLIP</span>
                  <span className="text-sm font-semibold text-gray-900">0.87</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '87%' }}></div>
                </div>
              </div>
              <div className="bg-white rounded-lg p-3 border border-gray-200">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-xs font-medium text-gray-700">ArcFace</span>
                  <span className="text-sm font-semibold text-gray-900">0.72</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '72%' }}></div>
                </div>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
                <div className="w-3 h-3 bg-green-500 rounded"></div>
                <span>0.8-1.0: Excellent</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
                <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                <span>0.6-0.8: Good</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <div className="w-3 h-3 bg-red-500 rounded"></div>
                <span>&lt;0.6: Needs Improvement</span>
              </div>
            </div>
          </div>

          {/* Metadata & Audit */}
          <div>
            <h2 className="text-sm font-semibold text-gray-900 mb-3">Metadata & Audit</h2>
            <div className="bg-white rounded-lg p-4 border border-gray-200 space-y-3">
              <div>
                <p className="text-xs font-medium text-gray-500 mb-1">Prompt</p>
                <p className="text-xs text-gray-900">Create a futuristic cityscape with neon lights and flying cars.</p>
              </div>
              <div className="pt-3 border-t border-gray-200 space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Model:</span>
                  <span className="text-gray-900 font-medium">SDXL-v1.5</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Seed:</span>
                  <span className="text-gray-900 font-medium">42857391</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Latency:</span>
                  <span className="text-gray-900 font-medium">2.35s</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">Generated:</span>
                  <span className="text-gray-900 font-medium">12:46 PM</span>
                </div>
              </div>
              <div className="pt-3 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-500 mb-1">Audit ID</p>
                <p className="text-xs text-gray-900 font-mono">AUD-7F8E9A2B</p>
              </div>
            </div>
            <button className="w-full mt-3 bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
              Export ZIP with Audit Data
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  export default RightPanel;
  