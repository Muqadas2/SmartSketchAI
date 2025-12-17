import Sidebar from "../components/Sidebar";
import TopBar from "../components/Topbar";
import Workspace from "../components/Workspace";
import RightPanel from "../components/RightPanel";

function Home() {
  return (
    <div className="h-screen flex flex-col bg-white">
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <Workspace />
        <RightPanel />
      </div>
    </div>
  );
}

export default Home;
