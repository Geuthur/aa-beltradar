// Third Party
import type { QueryKey } from "@tanstack/react-query";
import { queryKeys as baseQueryKeys } from "aa-geuthur-react";

export const SESSION_REFETCH_INTERVAL_MS = 30_000;

// `Menu`, `User` and `UserSettings` come from the package, so its hooks and the app share them.
export const queryKeys = {
    ...baseQueryKeys,
    Session: (publicID: string) => ["Session", publicID] as const,
    publicSessions: ["Public-Session"] as const,
    mySessions: (characterID?: number) => ["My-Sessions", characterID] as const,

    beltTimer: ["Belt-Timer"] as const,
    myBeltTimers: (characterID?: number) => ["My-Belt-Timers", characterID] as const,


    Snapshot: (publicID: string, identifier?: string | null) => ["Snapshot", publicID, identifier ?? "latest"] as const,
};

/** Lists and timers every create, modify and delete action refreshes unless a caller names its own keys. */
export const listQueryKeys: QueryKey[] = [
    queryKeys.publicSessions,
    ["My-Sessions"],
    queryKeys.beltTimer,
    ["My-Belt-Timers"],
];
