// Third Party
import { beforeEach, describe, expect, it, vi } from 'vitest';

// AA Belt Radar
import { apiClient } from '@/Api/Api';
import {
    loadSession,
    loadSnapshot,
    sessionQueryKeys,
} from '@/Api/calls/session';

describe('sessionQueryKeys', () => {
    it('creates session key with publicID', () => {
        expect(sessionQueryKeys.session('sess-123')).toEqual(['Session', 'sess-123']);
    });

    it('creates snapshot key falling back to "latest" if identifier is not provided', () => {
        expect(sessionQueryKeys.snapshot('sess-123')).toEqual(['Snapshot', 'sess-123', 'latest']);
        expect(sessionQueryKeys.snapshot('sess-123', null)).toEqual(['Snapshot', 'sess-123', 'latest']);
        expect(sessionQueryKeys.snapshot('sess-123', 'snap-5')).toEqual(['Snapshot', 'sess-123', 'snap-5']);
    });
});

describe('Session API calls', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
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

/** Every call of `calls/session.ts`: [name, HTTP method, call, fixed text]. */
const calls: [string, Method, () => Promise<unknown>, string][] = [
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
