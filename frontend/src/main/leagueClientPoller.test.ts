/**
 * Unit tests for LeagueClientPoller.
 */

import { LeagueClientPoller } from '../main/leagueClientPoller';
import { ChampSelectSession } from '../shared/types';

const MOCK_SESSION: ChampSelectSession = {
  localPlayerCellId: 0,
  myTeam: [{ cellId: 0, championId: 157, assignedPosition: 'MIDDLE' }],
  theirTeam: [{ cellId: 5, championId: 238 }],
};

// Helper: flush all pending promises and microtasks
const flushPromises = (): Promise<void> =>
  new Promise((resolve) => setImmediate(resolve));

// Mock global fetch
const mockFetch = jest.fn();
global.fetch = mockFetch as typeof fetch;

beforeEach(() => {
  jest.useFakeTimers({ doNotFake: ['setImmediate'] });
  mockFetch.mockReset();
});

afterEach(() => {
  jest.useRealTimers();
});

describe('LeagueClientPoller', () => {
  it('calls onChampSelectEntered when client returns a session', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => MOCK_SESSION,
    } as Response);

    const onEntered = jest.fn();
    const onExited = jest.fn();

    const poller = new LeagueClientPoller({
      pollIntervalMs: 1000,
      onChampSelectEntered: onEntered,
      onChampSelectExited: onExited,
    });

    poller.start();
    jest.advanceTimersByTime(1100);
    await flushPromises();

    expect(onEntered).toHaveBeenCalledWith(MOCK_SESSION);
    expect(onExited).not.toHaveBeenCalled();
    poller.stop();
  });

  it('calls onChampSelectExited when session disappears', async () => {
    // First poll: in champ select
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => MOCK_SESSION,
      } as Response)
      // Second poll: not in champ select
      .mockResolvedValueOnce({
        ok: false,
        json: async () => null,
      } as unknown as Response);

    const onEntered = jest.fn();
    const onExited = jest.fn();

    const poller = new LeagueClientPoller({
      pollIntervalMs: 1000,
      onChampSelectEntered: onEntered,
      onChampSelectExited: onExited,
    });

    poller.start();

    jest.advanceTimersByTime(1100);
    await flushPromises();

    jest.advanceTimersByTime(1000);
    await flushPromises();

    expect(onExited).toHaveBeenCalled();
    poller.stop();
  });

  it('does not call onChampSelectExited when never entered', async () => {
    mockFetch.mockResolvedValue({
      ok: false,
      json: async () => null,
    } as unknown as Response);

    const onExited = jest.fn();
    const poller = new LeagueClientPoller({
      pollIntervalMs: 1000,
      onChampSelectEntered: jest.fn(),
      onChampSelectExited: onExited,
    });

    poller.start();
    jest.advanceTimersByTime(3100);
    await flushPromises();

    expect(onExited).not.toHaveBeenCalled();
    poller.stop();
  });

  it('stop() prevents further polling', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => MOCK_SESSION,
    } as Response);

    const onEntered = jest.fn();
    const poller = new LeagueClientPoller({
      pollIntervalMs: 1000,
      onChampSelectEntered: onEntered,
      onChampSelectExited: jest.fn(),
    });

    poller.start();
    poller.stop();
    jest.advanceTimersByTime(5000);
    await flushPromises();

    expect(onEntered).not.toHaveBeenCalled();
  });
});
