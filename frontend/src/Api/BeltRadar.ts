// Third Party
import axios from "axios";

// AA Belt Radar
import type { components } from "@/Api/OpenApi";

export async function loadUserData(): Promise<{ user: components["schemas"]["UserData"] }> {
  const api = await axios.get(`/beltradar/api/view/user/`);
  const data = {
    user: api.data,
  };
  return data;
}

export async function loadPublicSessions(): Promise<components["schemas"]["BeltSurveySessionSchema"][]> {
  const api = await axios.get(`/beltradar/api/view/public-sessions/`);
  return api.data;
}

export async function loadMySessions(characterID: number): Promise<components["schemas"]["BeltSurveySessionSchema"][]> {
  const api = await axios.get(`/beltradar/api/view/my-sessions/${characterID}/`);
  return api.data;
}

export async function loadBeltTimers(): Promise<components["schemas"]["BeltTimerSchema"][]> {
  const api = await axios.get(`/beltradar/api/view/belt-timers/`);
  return api.data;
}

export async function loadMyBeltTimers(characterID: number): Promise<components["schemas"]["BeltTimerSchema"][]> {
  const api = await axios.get(`/beltradar/api/view/my-belt-timers/${characterID}/`);
  return api.data;
}

export async function loadSession(publicID: string): Promise<components["schemas"]["SessionSchema"]> {
  const api = await axios.get(`/beltradar/api/view/session/${publicID}/stats/`);
  return api.data;
}

export async function loadSnapshot(publicID: string): Promise<components["schemas"]["SnapShotSchema"]> {
  const api = await axios.get(`/beltradar/api/view/session/${publicID}/snapshot/last_snapshot/`);
  return api.data;
}

export async function loadMenu(): Promise<components["schemas"]["MenuSchema"]> {
  const api = await axios.get(`/beltradar/api/view/menu/`);
  return api.data;
}
