/**
 * Renderer entry point — mounts the overlay UI.
 */

import { RecommendResponse } from '../shared/types';
import { renderOverlay } from './overlay';

// Declare the API injected by the preload script
declare global {
  interface Window {
    runeAPI: {
      onRecommendation: (cb: (r: RecommendResponse) => void) => void;
      onChampSelectUpdate: (cb: (session: unknown) => void) => void;
      onError: (cb: (msg: string) => void) => void;
      importRunes: (page: RecommendResponse['runes']) => Promise<{ success: boolean }>;
      removeAllListeners: () => void;
    };
  }
}

const root = document.getElementById('app');
if (!root) throw new Error('Missing #app element');

// Render initial waiting state
root.innerHTML = renderOverlay(null);

// Update UI when a recommendation arrives
window.runeAPI.onRecommendation((recommendation) => {
  root.innerHTML = renderOverlay(recommendation);

  const btn = document.getElementById('import-btn');
  if (btn) {
    btn.addEventListener('click', async () => {
      btn.textContent = 'Importing…';
      btn.setAttribute('disabled', 'true');
      try {
        const result = await window.runeAPI.importRunes(recommendation.runes);
        btn.textContent = result.success ? '✓ Imported!' : '✗ Failed';
      } catch {
        btn.textContent = '✗ Error';
      }
    });
  }
});

// Hide overlay when champ select ends
window.runeAPI.onChampSelectUpdate((session) => {
  if (!session) {
    root.innerHTML = renderOverlay(null);
  }
});

window.runeAPI.onError((msg) => {
  root.innerHTML = `<div class="error">Error: ${msg}</div>`;
});
