import { useUser } from "../context/UserContext";

export default function UserToggle() {
  const { users, activeUser, setActiveUser, view, setView } = useUser();

  if (users.length < 2) return null;

  const handleUserClick = (key) => {
    setActiveUser(key);
    setView("dashboard");
  };

  const handleCompareClick = () => {
    setView("compare");
  };

  return (
    <div className="flex items-center bg-white/5 border border-white/10 rounded-lg p-0.5">
      {users.map((u) => (
        <button
          key={u.key}
          onClick={() => handleUserClick(u.key)}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-all ${
            view === "dashboard" && activeUser === u.key
              ? "bg-gradient-to-r from-oura-blue to-oura-purple text-white shadow-sm"
              : "text-gray-400 hover:text-white"
          }`}
        >
          {u.name}
        </button>
      ))}
      <div className="w-px h-4 bg-white/10 mx-0.5" />
      <button
        onClick={handleCompareClick}
        className={`px-3 py-1 text-sm font-medium rounded-md transition-all ${
          view === "compare"
            ? "bg-gradient-to-r from-oura-blue to-[#FF2D55] text-white shadow-sm"
            : "text-gray-400 hover:text-white"
        }`}
      >
        Compare
      </button>
    </div>
  );
}
