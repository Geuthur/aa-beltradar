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
  const { data, error } = await apiClient.GET("/beltradar/api/view/menu/");
  if (error || !data) {
    throw new Error("Failed to load menu");
  }
  return data;
}

export async function updateUserSettings(settings: { disable_notifications: boolean }): Promise<{ success: boolean; message?: string }> {
  const body = new FormData();
  if (settings.disable_notifications) {
    body.append("disable_notifications", "on");
  }

  const { data, error } = await apiClient.POST("/beltradar/api/modify/user/settings/", {
    body: body as never,
  });

  if (error || !data || (data as { success?: boolean }).success !== true) {
    throw new Error((data as { message?: string } | undefined)?.message ?? "Failed to update user settings");
  }
  return data as { success: boolean; message?: string };
}
