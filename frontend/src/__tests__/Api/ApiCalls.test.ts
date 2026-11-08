// Third Party
import { beforeEach, describe, expect, it, vi } from 'vitest';

// AA Belt Radar
import { apiClient } from '@/Api/Api';
import {
    loadBeltTimers,
    loadMenu,
    loadMyBeltTimers,
    loadMySessions,
    loadPublicSessions,
    loadSession,
    loadSnapshot,
    loadUserSettings,
    updateUserSettings,
} from '@/Api/ApiCalls';

describe('BeltRadar API client functions', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    describe('loadPublicSessions', () => {
        it('returns list of public sessions', async () => {
            const mockSessions = [{ public_id: 'sess-1', name: 'Public Belt 1' }];
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockSessions,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadPublicSessions();
            expect(result).toEqual(mockSessions);
            expect(apiClient.GET).toHaveBeenCalledWith('/beltradar/api/view/public-sessions/');
        });
    });

    describe('loadMySessions', () => {
        it('calls endpoint with character_id path param', async () => {
            const mockSessions = [{ public_id: 'sess-2', name: 'My Belt' }];
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockSessions,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadMySessions(12345);
            expect(result).toEqual(mockSessions);
            expect(apiClient.GET).toHaveBeenCalledWith('/beltradar/api/view/my-sessions/{character_id}/', {
                params: { path: { character_id: 12345 } },
            });
        });
    });

    describe('loadBeltTimers and loadMyBeltTimers', () => {
        it('loadBeltTimers calls /view/belt-timers/', async () => {
            const mockTimers = [{ public_id: 't-1', belt_name: 'Belt Alpha' }];
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockTimers,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadBeltTimers();
            expect(result).toEqual(mockTimers);
        });

        it('loadMyBeltTimers calls with character_id', async () => {
            const mockTimers = [{ public_id: 't-2', belt_name: 'Belt Beta' }];
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockTimers,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadMyBeltTimers(999);
            expect(result).toEqual(mockTimers);
            expect(apiClient.GET).toHaveBeenCalledWith('/beltradar/api/view/my-belt-timers/{character_id}/', {
                params: { path: { character_id: 999 } },
            });
        });
    });

    describe('loadSession', () => {
        it('calls /view/session/{public_id}/stats/ with public_id', async () => {
            const mockStats = { public_id: 'sess-abc', has_timer: true };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockStats,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadSession('sess-abc');
            expect(result).toEqual(mockStats);
            expect(apiClient.GET).toHaveBeenCalledWith('/beltradar/api/view/session/{public_id}/stats/', {
                params: { path: { public_id: 'sess-abc' } },
            });
        });
    });

    describe('loadSnapshot', () => {
        it('calls endpoint with public_id and optional identifier', async () => {
            const mockSnapshot = { snapshot: { identifier: 'snap-1' } };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockSnapshot,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadSnapshot('sess-abc', 'snap-1');
            expect(result).toEqual(mockSnapshot);
            expect(apiClient.GET).toHaveBeenCalledWith(
                '/beltradar/api/view/session/{public_id}/snapshot/last_snapshot/',
                {
                    params: {
                        path: { public_id: 'sess-abc' },
                        query: { identifier: 'snap-1' },
                    },
                },
            );
        });
    });

    describe('loadMenu', () => {
        it('calls /menu/ and returns data', async () => {
            const mockMenu = { left_links: [], right_links: [] };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockMenu,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadMenu();
            expect(result).toEqual(mockMenu);
            expect(apiClient.GET).toHaveBeenCalledWith('/beltradar/api/menu/');
        });
    });

    describe('loadUserSettings', () => {
        it('calls /settings/ and returns the settings', async () => {
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: { disable_notifications: true },
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadUserSettings();
            expect(result).toEqual({ disable_notifications: true });
            expect(apiClient.GET).toHaveBeenCalledWith('/beltradar/api/settings/');
        });

        it('throws error when GET fails', async () => {
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { error: 'Permission Denied.' },
                response: new Response(),
            } as never);

            await expect(loadUserSettings()).rejects.toThrow('Failed to load user settings');
        });
    });

    describe('updateUserSettings', () => {
        it('sends the settings as PUT body and returns them', async () => {
            vi.spyOn(apiClient, 'PUT').mockResolvedValueOnce({
                data: { disable_notifications: true },
                error: undefined,
                response: new Response(),
            } as never);

            const result = await updateUserSettings({ disable_notifications: true });
            expect(result).toEqual({ disable_notifications: true });
            expect(apiClient.PUT).toHaveBeenCalledWith('/beltradar/api/settings/', {
                body: { disable_notifications: true },
            });
        });

        it('throws error when update fails', async () => {
            vi.spyOn(apiClient, 'PUT').mockResolvedValueOnce({
                data: undefined,
                error: { error: 'Permission Denied.' },
                response: new Response(),
            } as never);

            await expect(updateUserSettings({ disable_notifications: false })).rejects.toThrow(
                'Failed to update user settings',
            );
        });
    });
});
