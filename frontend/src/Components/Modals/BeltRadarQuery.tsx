// Third Party
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { QueryKey } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';

// AA Belt Radar
import { queryKeys } from "@/Api/query";

type FormData = Record<string, string | boolean>;

function buildHeaders() {
    return {
        'X-CSRFToken': Cookies.get('csrftoken') ?? '',
    };
}

/** Mutation für Delete / Update / Bestätigungen (ohne Body) */
export function useApproveMutation(queryKey?: QueryKey | QueryKey[]) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (url: string) => {
            const response = await axios.post(url, {}, {
                withCredentials: true,
                headers: buildHeaders(),
            });

            if (response.data.success !== true) {
                throw new Error(response.data.message ?? 'Unknown error');
            }
            return response.data;
        },
        onSuccess: async () => {
            if (queryKey) {
                if (Array.isArray(queryKey) && Array.isArray(queryKey[0])) {
                    await Promise.all(
                        (queryKey as QueryKey[]).map((key) =>
                            queryClient.invalidateQueries({ queryKey: key, refetchType: 'all' })
                        )
                    );
                } else {
                    await queryClient.invalidateQueries({ queryKey: queryKey as QueryKey, refetchType: 'all' });
                }
            } else {
                await Promise.all([
                    queryClient.invalidateQueries({ queryKey: queryKeys.publicSessions, refetchType: 'all' }),
                    queryClient.invalidateQueries({ queryKey: ["My-Sessions"], refetchType: 'all' }),
                    queryClient.invalidateQueries({ queryKey: queryKeys.beltTimer, refetchType: 'all' }),
                    queryClient.invalidateQueries({ queryKey: ["My-Belt-Timers"], refetchType: 'all' }),
                ]);
            }
        },
    });
}

/** Mutation für Formulare (mit Formulardaten als URLSearchParams) */
export function useFormApproveMutation(queryKey?: QueryKey | QueryKey[]) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({ url, formData = {} }: { url: string; formData?: FormData }) => {
            const body = new URLSearchParams();
            for (const [key, value] of Object.entries(formData)) {
                if (typeof value === 'boolean') {
                    if (value) body.append(key, 'on');
                } else {
                    body.append(key, value);
                }
            }

            const response = await axios.post(url, body, {
                withCredentials: true,
                headers: {
                    ...buildHeaders(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            if (response.data.success !== true) {
                throw new Error(response.data.message ?? 'Unknown error');
            }
            return response.data;
        },
        onSuccess: async () => {
            if (queryKey) {
                if (Array.isArray(queryKey) && Array.isArray(queryKey[0])) {
                    await Promise.all(
                        (queryKey as QueryKey[]).map((key) =>
                            queryClient.invalidateQueries({ queryKey: key, refetchType: 'all' })
                        )
                    );
                } else {
                    await queryClient.invalidateQueries({ queryKey: queryKey as QueryKey, refetchType: 'all' });
                }
            } else {
                // Standardmäßig alle Sessions und Timer invalidieren
                await Promise.all([
                    queryClient.invalidateQueries({ queryKey: queryKeys.publicSessions, refetchType: 'all' }),
                    queryClient.invalidateQueries({ queryKey: ["My-Sessions"], refetchType: 'all' }),
                    queryClient.invalidateQueries({ queryKey: queryKeys.beltTimer, refetchType: 'all' }),
                    queryClient.invalidateQueries({ queryKey: ["My-Belt-Timers"], refetchType: 'all' }),
                ]);
            }
        },
    });
}
