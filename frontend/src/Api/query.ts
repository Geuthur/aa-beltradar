export const queryKeys = {
    Session: (publicID: string) => ["Session", publicID] as const,
    publicSessions: ["Public-Session"] as const,
    mySessions: (characterID?: number) => ["My-Sessions", characterID] as const,

    beltTimer: ["Belt-Timer"] as const,
    myBeltTimers: (characterID?: number) => ["My-Belt-Timers", characterID] as const,


    Snapshot: (publicID: string) => ["Snapshot", publicID] as const,
    Menu: ["Menu"] as const,
    User: ["User"] as const,
};
