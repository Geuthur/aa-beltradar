// Third Party
import type { QueryKey } from "@tanstack/react-query";
import { apiErrorMessage } from "aa-geuthur-react";

// AA Belt Radar
import { apiClient } from "@/Api/Api";
import type { components } from "@/Api/OpenApi";

/** Query keys of the belt radar list pages (public and own sessions and belt timers). */
export const radarQueryKeys = {
  publicSessions: ["Public-Session"] as const,
  mySessions: (characterID?: number) => ["My-Sessions", characterID] as const,
  beltTimers: ["Belt-Timer"] as const,
  myBeltTimers: (characterID?: number) => ["My-Belt-Timers", characterID] as const,
};

/** Lists and timers every create, modify and delete action refreshes unless a caller names its own keys. */
export const listQueryKeys: QueryKey[] = [
  radarQueryKeys.publicSessions,
  ["My-Sessions"],
  radarQueryKeys.beltTimers,
  ["My-Belt-Timers"],
];

export async function loadPublicSessions(): Promise<components["schemas"]["SessionSchema"][]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/public-sessions/");
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load public sessions"));
  }
  return data;
}

export async function loadMySessions(characterID: number): Promise<components["schemas"]["SessionSchema"][]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/my-sessions/{character_id}/", {
    params: {
      path: { character_id: characterID },
    },
  });
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load my sessions"));
  }
  return data;
}

export async function loadBeltTimers(): Promise<components["schemas"]["BeltTimerSchema"][]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/belt-timers/");
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load belt timers"));
  }
  return data;
}

export async function loadMyBeltTimers(characterID: number): Promise<components["schemas"]["BeltTimerSchema"][]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/my-belt-timers/{character_id}/", {
    params: {
      path: { character_id: characterID },
    },
  });
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load my belt timers"));
  }
  return data;
}
