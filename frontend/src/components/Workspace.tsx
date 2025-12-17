function Workspace() {
    return (
      <div className="flex-1 flex flex-col bg-white overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Welcome Message */}
          <div className="max-w-3xl mx-auto">
            <div className="text-center py-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">Welcome to SmartSketch AI</h2>
              <p className="text-gray-600">AI-powered image generation tool</p>
            </div>
          </div>

          {/* User Message */}
          <div className="max-w-3xl mx-auto">
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-900">Create a futuristic cityscape with neon lights and flying cars.</p>
                </div>
              </div>
            </div>
          </div>

          {/* AI Assistant Response */}
          <div className="max-w-3xl mx-auto">
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <div className="mb-2">
                  <span className="text-sm font-medium text-gray-700">AI Assistant</span>
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg h-64 flex items-center justify-center bg-white">
                    <span className="text-gray-500 text-sm">Futuristic Cityscape with Neon Lights</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="max-w-3xl mx-auto">
            <input
              type="text"
              placeholder="Type your prompt here... Describe the image you want to create."
              className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            />
          </div>
        </div>
      </div>
    );
  }
  
  export default Workspace;
  