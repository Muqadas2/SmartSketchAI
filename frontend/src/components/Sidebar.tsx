import { Link, useLocation } from 'react-router-dom';

function Sidebar() {
  const location = useLocation();
  
  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Chat History</h2>
        <ul className="space-y-2">
          <li className="text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-lg cursor-pointer transition-colors">
            Sunset landscape photo
          </li>
          <li className="text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-lg cursor-pointer transition-colors">
            Portrait photography
          </li>
          <li className="text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-lg cursor-pointer transition-colors">
            Abstract art creation
          </li>
        </ul>
      </div>
      
      <div className="p-4 mt-auto border-t border-gray-200">
        <h2 className="text-sm font-semibold text-gray-700 mb-3">Navigate</h2>
        <ul className="space-y-1">
          <li>
            <Link
              to="/"
              className={`text-sm px-3 py-2 rounded-lg transition-colors block ${
                location.pathname === '/'
                  ? 'text-gray-900 bg-gray-100 font-medium'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Chat Interface
            </Link>
          </li>
          <li>
            <Link
              to="/settings"
              className={`text-sm px-3 py-2 rounded-lg transition-colors block ${
                location.pathname.startsWith('/settings')
                  ? 'text-gray-900 bg-gray-100 font-medium'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              Settings
            </Link>
          </li>
          <li className="text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-lg cursor-pointer transition-colors">
            Help & Support
          </li>
        </ul>
      </div>
    </div>
  );
}

export default Sidebar;
  