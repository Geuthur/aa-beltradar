// Third Party
import { beforeEach, describe, expect, it, vi } from 'vitest';

// AA Belt Radar
import { apiClient } from '@/Api/Api';
import {
    listQueryKeys,
    loadBeltTimers,
    loadMyBeltTimers,
    loadMySessions,
    loadPublicSessions,
    radarQueryKeys,
} from '@/Api/calls/radar';

describe('radarQueryKeys', () => {
    it('provides the list keys', () => {
        expect(radarQueryKeys.publicSessions).toEqual(['Public-Session']);
        expect(radarQueryKeys.beltTimers).toEqual(['Belt-Timer']);
    });

    it('creates mySessions key with characterID', () => {
        expect(radarQueryKeys.mySessions(42)).toEqual(['My-Sessions', 42]);
        expect(radarQueryKeys.mySessions(undefined)).toEqual(['My-Sessions', undefined]);
    });

    it('creates myBeltTimers key with characterID', () => {
        expect(radarQueryKeys.myBeltTimers(99)).toEqual(['My-Belt-Timers', 99]);
        expect(radarQueryKeys.myBeltTimers(undefined)).toEqual(['My-Belt-Timers', undefined]);
    });

    it('lists the keys every create, modify and delete action refreshes', () => {
        expect(listQueryKeys).toEqual([['Public-Session'], ['My-Sessions'], ['Belt-Timer'], ['My-Belt-Timers']]);
    });
});

describe('Radar API calls', () => {
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
});

type Method = 'GET' | 'POST' | 'DELETE';

/** Every call of `calls/radar.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
    ['loadPublicSessions', 'GET', () => loadPublicSessions(), 'Failed to load public sessions'],
    ['loadMySessions', 'GET', () => loadMySessions(1001), 'Failed to load my sessions'],
    ['loadBeltTimers', 'GET', () => loadBeltTimers(), 'Failed to load belt timers'],
    ['loadMyBeltTimers', 'GET', () => loadMyBeltTimers(1001), 'Failed to load my belt timers'],
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
