import { createContext, useContext, useState } from "react";

const DateRangeContext = createContext();

export function DateRangeProvider({ children }) {
  const [days, setDays] = useState(7);

  return (
    <DateRangeContext.Provider value={{ days, setDays }}>
      {children}
    </DateRangeContext.Provider>
  );
}

export function useDateRange() {
  const context = useContext(DateRangeContext);
  if (!context) {
    throw new Error("useDateRange must be used within DateRangeProvider");
  }
  return context;
}
