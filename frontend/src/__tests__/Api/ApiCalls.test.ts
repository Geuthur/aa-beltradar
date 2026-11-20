// Third Party
import { beforeEach, describe, expect, it, vi } from 'vitest';

// AA Belt Radar
import { apiClient } from '@/Api/Api';
import {
    loadBeltTimers,
    loadMyBeltTimers,
    loadMySessions,
    loadPublicSessions,
    loadSession,
    loadSnapshot,
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
});

type Method = 'GET' | 'POST' | 'DELETE';

/** Every call of `ApiCalls.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
    ['loadPublicSessions', 'GET', () => loadPublicSessions(), 'Failed to load public sessions'],
    ['loadMySessions', 'GET', () => loadMySessions(1001), 'Failed to load my sessions'],
    ['loadBeltTimers', 'GET', () => loadBeltTimers(), 'Failed to load belt timers'],
    ['loadMyBeltTimers', 'GET', () => loadMyBeltTimers(1001), 'Failed to load my belt timers'],
    ['loadSession', 'GET', () => loadSession('sess-1'), 'Failed to load session'],
    ['loadSnapshot', 'GET', () => loadSnapshot('sess-1', 'snap-1'), 'Failed to load snapshot'],
];

const failWith = (method: Method, error: unknown) =>
    vi.spyOn(apiClient, method).mockResolvedValueOnce({
        data: undefined,
        error,
        response: new Response(),
    } as never);

describe('API calls on errors', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    describe.each(calls)('%s', (_name, method, call, fixedText) => {
        it('should throw the message of the API when the request fails', async () => {
            // Test Data
            failWith(method, { error: 'Permission Denied' });

            // Test Action & Expected Result
            await expect(call()).rejects.toThrow('Permission Denied');
        });

        it('should throw the fixed text when the API sent no message', async () => {
            // Test Data
            failWith(method, {});

            // Test Action & Expected Result
            await expect(call()).rejects.toThrow(fixedText);
        });
    });
});
