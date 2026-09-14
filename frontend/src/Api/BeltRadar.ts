// Third Party
import axios from "axios";

// AA Belt Radar
import type { components } from "./OpenApi";

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
