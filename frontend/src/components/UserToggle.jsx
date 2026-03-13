import { useUser } from "../context/UserContext";

export default function UserToggle() {
  const { users, activeUser, setActiveUser } = useUser();

  if (users.length < 2) return null;

  return (
    <div className="flex items-center bg-white/5 border border-white/10 rounded-lg p-0.5">
      {users.map((u) => (
        <button
          key={u.key}
          onClick={() => setActiveUser(u.key)}
          className={`px-3 py-1 text-sm font-medium rounded-md transition-all ${
            activeUser === u.key
              ? "bg-gradient-to-r from-oura-blue to-oura-purple text-white shadow-sm"
              : "text-gray-400 hover:text-white"
          }`}
        >
          {u.name}
        </button>
      ))}
    </div>
  );
}
