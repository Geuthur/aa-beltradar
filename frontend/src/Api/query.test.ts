// Third Party
import { describe, expect, it } from 'vitest';

// AA Belt Radar
import { queryKeys } from '@/Api/query';

describe('queryKeys', () => {
    it('creates correct Session query key', () => {
        expect(queryKeys.Session('sess-123')).toEqual(['Session', 'sess-123']);
    });

    it('provides static query keys', () => {
        expect(queryKeys.publicSessions).toEqual(['Public-Session']);
        expect(queryKeys.beltTimer).toEqual(['Belt-Timer']);
        expect(queryKeys.Menu).toEqual(['Menu']);
        expect(queryKeys.User).toEqual(['User']);
    });

    it('creates mySessions query key with and without characterID', () => {
        expect(queryKeys.mySessions(42)).toEqual(['My-Sessions', 42]);
        expect(queryKeys.mySessions(undefined)).toEqual(['My-Sessions', undefined]);
    });

    it('creates myBeltTimers query key with and without characterID', () => {
        expect(queryKeys.myBeltTimers(99)).toEqual(['My-Belt-Timers', 99]);
        expect(queryKeys.myBeltTimers(undefined)).toEqual(['My-Belt-Timers', undefined]);
    });

    it('creates Snapshot query key falling back to "latest" if identifier is not provided', () => {
        expect(queryKeys.Snapshot('sess-123')).toEqual(['Snapshot', 'sess-123', 'latest']);
        expect(queryKeys.Snapshot('sess-123', null)).toEqual(['Snapshot', 'sess-123', 'latest']);
        expect(queryKeys.Snapshot('sess-123', 'snap-5')).toEqual(['Snapshot', 'sess-123', 'snap-5']);
    });
});
