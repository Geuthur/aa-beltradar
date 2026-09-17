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
    loadUserData,
    updateUserSettings,
} from '@/Api/BeltRadar';

describe('BeltRadar API client functions', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    describe('loadUserData', () => {
        it('returns user data on successful GET', async () => {
            const mockUser = { user_id: 1, character_id: 42, character_name: 'Test Pilot' };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockUser,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadUserData();
            expect(result).toEqual({ user: mockUser });
            expect(apiClient.GET).toHaveBeenCalledWith('/beltradar/api/view/user/');
        });

        it('throws error when GET fails or returns no data', async () => {
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { status: 500 },
                response: new Response(),
            } as never);

            await expect(loadUserData()).rejects.toThrow('Failed to load user data');
        });
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
        it('calls /view/menu/ and returns data', async () => {
            const mockMenu = { links: [] };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockMenu,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadMenu();
            expect(result).toEqual(mockMenu);
            expect(apiClient.GET).toHaveBeenCalledWith('/beltradar/api/view/menu/');
        });
    });

    describe('updateUserSettings', () => {
        it('submits FormData with disable_notifications and returns success', async () => {
            vi.spyOn(apiClient, 'POST').mockResolvedValueOnce({
                data: { success: true },
                error: undefined,
                response: new Response(),
            } as never);

            const result = await updateUserSettings({ disable_notifications: true });
            expect(result).toEqual({ success: true });
            expect(apiClient.POST).toHaveBeenCalledWith('/beltradar/api/modify/user/settings/', expect.any(Object));
        });

        it('throws error when update fails', async () => {
            vi.spyOn(apiClient, 'POST').mockResolvedValueOnce({
                data: { success: false, message: 'Permission denied' },
                error: undefined,
                response: new Response(),
            } as never);

            await expect(updateUserSettings({ disable_notifications: false })).rejects.toThrow('Permission denied');
        });
    });
});
