// AA Belt Radar
import { apiClient } from "@/Api/Api";
import type { components } from "@/Api/OpenApi";
import { ProjectName } from "@/constants";

export async function loadPublicSessions(): Promise<components["schemas"]["SessionSchema"][]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/public-sessions/");
  if (error || !data) {
    throw new Error("Failed to load public sessions");
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

export async function loadSession(publicID: string): Promise<components["schemas"]["SessionStatsSchema"]> {
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

export async function loadSnapshot(
  publicID: string,
  identifier?: string | null
): Promise<components["schemas"]["SnapShotSchema"]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/session/{public_id}/snapshot/last_snapshot/", {
    params: {
      path: { public_id: publicID },
      query: identifier ? { identifier } : undefined,
    },
  });
  if (error || !data) {
    throw new Error("Failed to load snapshot");
  }
  return data;
}

export async function loadMenu(): Promise<components["schemas"]["MenuSchema"]> {
  const { data, error } = await apiClient.GET(`/${ProjectName}/api/menu/`);
  if (error || !data) {
    throw new Error("Failed to load menu");
  }
  return data;
}

export async function loadUserSettings(): Promise<components["schemas"]["UserSettingsSchema"]> {
  const { data, error } = await apiClient.GET(`/${ProjectName}/api/settings/`);
  if (error || !data) {
    throw new Error("Failed to load user settings");
  }
  return data;
}

export async function updateUserSettings(
  settings: components["schemas"]["UserSettingsUpdateRequest"],
): Promise<components["schemas"]["UserSettingsSchema"]> {
  const { data, error } = await apiClient.PUT(`/${ProjectName}/api/settings/`, {
    body: settings,
  });
  if (error || !data) {
    throw new Error("Failed to update user settings");
  }
  return data;
}
