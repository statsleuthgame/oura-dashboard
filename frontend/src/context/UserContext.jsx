import { createContext, useContext, useState, useEffect } from "react";

const UserContext = createContext();

export function UserProvider({ children }) {
  const [users, setUsers] = useState([]);
  const [activeUser, setActiveUser] = useState("cody");
  const [view, setView] = useState("dashboard"); // "dashboard" | "compare"

  useEffect(() => {
    fetch("/api/users")
      .then((res) => res.json())
      .then((data) => {
        setUsers(data);
        if (data.length > 0 && !data.find((u) => u.key === activeUser)) {
          setActiveUser(data[0].key);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <UserContext.Provider value={{ users, activeUser, setActiveUser, view, setView }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within UserProvider");
  }
  return context;
}
