// AA Belt Radar
import { apiClient } from "@/Api/Api";
import type { components } from "@/Api/OpenApi";

export async function loadUserData(): Promise<{ user: components["schemas"]["UserData"] }> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/user/");
  if (error || !data) {
    throw new Error("Failed to load user data");
  }
  return { user: data };
}

export async function loadPublicSessions(): Promise<components["schemas"]["BeltSurveySessionSchema"][]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/public-sessions/");
  if (error || !data) {
    throw new Error("Failed to load public sessions");
  }
  return data;
}

export async function loadMySessions(characterID: number): Promise<components["schemas"]["BeltSurveySessionSchema"][]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/my-sessions/{character_id}/", {
    params: {
      path: { character_id: characterID },
    },
  });
  if (error || !data) {
    throw new Error("Failed to load my sessions");
  }
  return data;
}

export async function loadBeltTimers(): Promise<components["schemas"]["BeltTimerSchema"][]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/belt-timers/");
  if (error || !data) {
    throw new Error("Failed to load belt timers");
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
    throw new Error("Failed to load my belt timers");
  }
  return data;
}

export async function loadSession(publicID: string): Promise<components["schemas"]["SessionSchema"]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/session/{public_id}/stats/", {
    params: {
      path: { public_id: publicID },
    },
  });
  if (error || !data) {
    throw new Error("Failed to load session");
  }
  return data;
}

export async function loadSnapshot(publicID: string): Promise<components["schemas"]["SnapShotSchema"]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/session/{public_id}/snapshot/last_snapshot/", {
    params: {
      path: { public_id: publicID },
    },
  });
  if (error || !data) {
    throw new Error("Failed to load snapshot");
  }
  return data;
}

export async function loadMenu(): Promise<components["schemas"]["MenuSchema"]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/menu/");
  if (error || !data) {
    throw new Error("Failed to load menu");
  }
  return data;
}
