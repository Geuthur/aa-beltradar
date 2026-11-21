// Third Party
import { apiErrorMessage } from "aa-geuthur-react";

// AA Belt Radar
import { apiClient } from "@/Api/Api";
import type { components } from "@/Api/OpenApi";

export const SESSION_REFETCH_INTERVAL_MS = 30_000;

/** Query keys of the session page. */
export const sessionQueryKeys = {
  session: (publicID: string) => ["Session", publicID] as const,
  snapshot: (publicID: string, identifier?: string | null) => ["Snapshot", publicID, identifier ?? "latest"] as const,
};

export async function loadSession(publicID: string): Promise<components["schemas"]["SessionStatsSchema"]> {
  const { data, error } = await apiClient.GET("/beltradar/api/view/session/{public_id}/stats/", {
    params: {
      path: { public_id: publicID },
    },
  });
  if (error || !data) {
    throw new Error(apiErrorMessage(error, "Failed to load session"));
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
    throw new Error(apiErrorMessage(error, "Failed to load snapshot"));
  }
  return data;
}
