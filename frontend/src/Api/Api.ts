// Third Party
import axios from "axios";
import Cookies from "js-cookie";
import createClient from "openapi-fetch";
import type { PathsWithMethod } from "openapi-typescript-helpers";

// AA Belt Radar
import type { paths } from "@/Api/OpenApi";

// Django's CSRF cookie is named "csrftoken", not axios's own default
// ("XSRF-TOKEN") - both must be set for axios to actually attach the header
// automatically. Set once here rather than duplicated per API module.
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";

export type GetEndpoint = PathsWithMethod<paths, "get">;

export const apiClient = createClient<paths>({
  baseUrl: "/",
  credentials: "same-origin",
});

apiClient.use({
  async onRequest({ request }) {
    const csrf = Cookies.get("csrftoken");
    if (csrf) {
      request.headers.set("X-CSRFToken", csrf);
    }
    return request;
  },
});

export const getCatApi = () => apiClient;
