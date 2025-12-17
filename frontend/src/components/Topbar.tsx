function TopBar() {
    return (
      <div className="h-16 border-b border-gray-200 bg-white flex items-center justify-between px-6">
        <h1 className="text-xl font-semibold text-gray-900">SmartSketch AI</h1>
        <button className="bg-gray-900 hover:bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          New Session
        </button>
      </div>
    );
  }
  
  export default TopBar;
  