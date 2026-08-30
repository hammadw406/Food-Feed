"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  getArea,
  getSessionId,
  getUserId,
  isOnboarded,
  resetIdentity,
} from "./identity";

interface SessionValue {
  userId: string | null;
  sessionId: string | null;
  area: string | null;
  onboarded: boolean;
  ready: boolean;
  reset: () => void;
}

const SessionContext = createContext<SessionValue>({
  userId: null,
  sessionId: null,
  area: null,
  onboarded: false,
  ready: false,
  reset: () => {},
});

export function SessionProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<Omit<SessionValue, "reset">>({
    userId: null,
    sessionId: null,
    area: null,
    onboarded: false,
    ready: false,
  });

  useEffect(() => {
    setState({
      userId: getUserId(),
      sessionId: getSessionId(),
      area: getArea(),
      onboarded: isOnboarded(),
      ready: true,
    });
  }, []);

  const value = useMemo<SessionValue>(
    () => ({
      ...state,
      reset: () => {
        resetIdentity();
        setState((s) => ({
          ...s,
          userId: getUserId(),
          sessionId: getSessionId(),
        }));
      },
    }),
    [state],
  );

  return (
    <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
  );
}

export function useSession() {
  return useContext(SessionContext);
}
