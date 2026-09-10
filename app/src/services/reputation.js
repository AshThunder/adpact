import { reactive, watch } from 'vue';
import { wagmiState } from './wagmi.js';

// Reactive state for the connected user's X profile
export const userXProfile = reactive({
  handle: '',
  score: 75,
  status: 'UNVERIFIED',
  reason: '',
  linkedAt: '',
  isLinked: false,
  loading: false,
  challengeCode: '',        // Pending verification challenge code
  verifiedViaTweet: false,  // True if ownership proven via tweet
});

// Reactive state for live X profile preview (fetched from X's public API)
export const xProfilePreview = reactive({
  handle: '',         // The handle this data belongs to
  displayName: '',
  avatarUrl: '',
  followers: null,    // Number or null
  following: null,
  description: '',
  verified: false,    // X blue check
  exists: null,       // true | false | null (unknown/loading)
  loading: false,
  error: '',
});

function resetProfilePreview() {
  xProfilePreview.handle = '';
  xProfilePreview.displayName = '';
  xProfilePreview.avatarUrl = '';
  xProfilePreview.followers = null;
  xProfilePreview.following = null;
  xProfilePreview.description = '';
  xProfilePreview.verified = false;
  xProfilePreview.exists = null;
  xProfilePreview.loading = false;
  xProfilePreview.error = '';
}

/**
 * Fetch live X profile data to prove the account exists.
 * Uses Twitter's public syndication endpoint (no API key needed).
 * Falls back to nitter instances if syndication is blocked.
 */
let _fetchAbortController = null;
let _fetchDebounceTimer = null;

export async function fetchXProfilePreview(handle) {
  const clean = (handle || '').replace('@', '').trim().toLowerCase();
  if (!clean || clean.length < 2) {
    resetProfilePreview();
    return;
  }

  // Don't re-fetch if we already have data for this handle
  if (xProfilePreview.handle === clean && xProfilePreview.exists === true) return;

  // Abort any in-flight request
  if (_fetchAbortController) _fetchAbortController.abort();
  _fetchAbortController = new AbortController();
  const signal = _fetchAbortController.signal;

  // Debounce: wait 400ms after user stops typing
  clearTimeout(_fetchDebounceTimer);
  await new Promise(resolve => {
    _fetchDebounceTimer = setTimeout(resolve, 400);
  });
  if (signal.aborted) return;

  xProfilePreview.loading = true;
  xProfilePreview.error = '';
  xProfilePreview.handle = clean;
  xProfilePreview.exists = null;

  try {
    // 1. Primary: Server-side proxy endpoint (/api/x-profile/:handle) - no CORS restrictions
    const proxyResp = await fetch(`/api/x-profile/${clean}`, {
      signal,
      headers: { 'Accept': 'application/json' }
    }).catch(() => null);

    if (signal.aborted) return;

    if (proxyResp && proxyResp.ok) {
      const data = await proxyResp.json();
      if (signal.aborted) return;

      if (data.exists === true) {
        xProfilePreview.displayName = data.displayName || `@${clean}`;
        xProfilePreview.avatarUrl = data.avatarUrl || '';
        xProfilePreview.followers = data.followers !== undefined ? data.followers : null;
        xProfilePreview.following = data.following !== undefined ? data.following : null;
        xProfilePreview.description = data.description || '';
        xProfilePreview.verified = !!data.verified;
        xProfilePreview.exists = true;
        xProfilePreview.loading = false;
        return;
      } else if (data.exists === false) {
        xProfilePreview.exists = false;
        xProfilePreview.error = data.error || `@${clean} does not exist on X`;
        xProfilePreview.loading = false;
        return;
      }
    }

    // 2. Secondary: Fallback to direct syndication API
    const syndicationUrl = `https://syndication.twitter.com/srv/timeline-profile/screen-name/${clean}`;
    const resp = await fetch(syndicationUrl, {
      signal,
      headers: { 'Accept': 'text/html' },
    }).catch(() => null);

    if (signal.aborted) return;

    if (resp && resp.ok) {
      const html = await resp.text();
      if (signal.aborted) return;

      const parsed = parseSyndicationProfile(html, clean);
      if (parsed) {
        xProfilePreview.displayName = parsed.displayName || `@${clean}`;
        xProfilePreview.avatarUrl = parsed.avatarUrl || '';
        xProfilePreview.followers = parsed.followers;
        xProfilePreview.following = parsed.following;
        xProfilePreview.description = parsed.description || '';
        xProfilePreview.verified = parsed.verified || false;
        xProfilePreview.exists = true;
        xProfilePreview.loading = false;
        return;
      }
    }

    // If we reach here, we could not confirm existence
    xProfilePreview.exists = false;
    xProfilePreview.error = `@${clean} does not exist or cannot be reached on X`;
    xProfilePreview.loading = false;
  } catch (err) {
    if (signal.aborted) return;
    console.warn('X profile preview fetch failed:', err);
    xProfilePreview.exists = false;
    xProfilePreview.error = `@${clean} does not exist or could not be verified on X.`;
    xProfilePreview.loading = false;
  }
}

/** Parse the syndication timeline page for profile data */
function parseSyndicationProfile(html, handle) {
  try {
    // The syndication page embeds a JSON data blob in a script tag
    // Look for __NEXT_DATA__ or embedded profile JSON
    const scriptMatch = html.match(/<script[^>]*id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/i);
    if (scriptMatch) {
      const data = JSON.parse(scriptMatch[1]);
      const user = data?.props?.pageProps?.timeline?.entries?.[0]?.content?.tweet?.user ||
                   data?.props?.pageProps?.user;
      if (user) {
        return {
          displayName: user.name || user.screen_name || handle,
          avatarUrl: (user.profile_image_url_https || user.profile_image_url || '').replace('_normal', '_400x400'),
          followers: user.followers_count ?? null,
          following: user.friends_count ?? null,
          description: user.description || '',
          verified: user.verified || user.is_blue_verified || false,
        };
      }
    }

    // Fallback: try extracting from embedded HTML/meta
    const nameMatch = html.match(/data-testid="UserName"[^>]*>([^<]+)/i) ||
                      html.match(/class="[^"]*UserName[^"]*"[^>]*>([^<]+)/i);
    const avatarMatch = html.match(/src="(https:\/\/pbs\.twimg\.com\/profile_images\/[^"]+)"/i);
    const followerMatch = html.match(/([\d,.]+)\s*<[^>]*>\s*Followers/i) ||
                          html.match(/([\d,.KkMm]+)\s*Followers/i);

    if (avatarMatch || nameMatch) {
      return {
        displayName: nameMatch ? nameMatch[1].trim() : `@${handle}`,
        avatarUrl: avatarMatch ? avatarMatch[1].replace('_normal', '_400x400') : '',
        followers: followerMatch ? parseFollowerCount(followerMatch[1]) : null,
        following: null,
        description: '',
        verified: false,
      };
    }
  } catch (e) {
    console.warn('Syndication parse failed:', e);
  }
  return null;
}

/** Parse follower count strings like "1.2M", "45.3K", "12,345" into numbers */
function parseFollowerCount(str) {
  if (!str) return null;
  const clean = str.replace(/,/g, '').trim();
  const multiplierMatch = clean.match(/^([\d.]+)\s*([KkMm]?)$/i);
  if (!multiplierMatch) return parseInt(clean, 10) || null;
  const num = parseFloat(multiplierMatch[1]);
  const suffix = multiplierMatch[2].toUpperCase();
  if (suffix === 'K') return Math.round(num * 1000);
  if (suffix === 'M') return Math.round(num * 1000000);
  return Math.round(num);
}

/** Format follower count for display: 1234 -> "1.2K", 1234567 -> "1.2M" */
export function formatFollowerCount(count) {
  if (count === null || count === undefined) return '—';
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return count.toString();
}

// Baseline score calculator factoring real follower metrics and handle characteristics
export function calculateBaselineScore(handle, followers = null) {
  if (!handle) return 60;

  if (followers !== null && followers !== undefined) {
    const f = Number(followers) || 0;
    if (f >= 1000000) return 96; // 1M+ Tier 1 Alpha Voice
    if (f >= 500000) return 92;  // 500K+
    if (f >= 100000) return 88;  // 100K+
    if (f >= 50000) return 84;   // 50K+
    if (f >= 10000) return 80;   // 10K+ High Signal
    if (f >= 5000) return 75;    // 5K+ Verified Voice
    if (f >= 1000) return 71;    // 1K+ Emerging
    return 65;                   // <1K New Account
  }

  const clean = handle.replace('@', '').toLowerCase();
  let hash = 0;
  for (let i = 0; i < clean.length; i++) {
    hash = (hash << 5) - hash + clean.charCodeAt(i);
    hash |= 0;
  }
  return 65 + (Math.abs(hash) % 25);
}

export function getScoreTier(score) {
  const s = Number(score) || 0;
  if (s >= 80) {
    return {
      label: 'Tier 1 / Alpha Voice',
      badgeClass: 'bg-fin-orange/15 text-fin-orange border-fin-orange/30',
      pillClass: 'bg-fin-orange text-white',
      color: 'var(--color-fin-orange, #FF5B22)',
      icon: 'stars',
      status: 'HIGH_SIGNAL',
    };
  }
  if (s >= 60) {
    return {
      label: 'Verified Crypto Voice',
      badgeClass: 'bg-brand-blue/15 text-brand-blue border-brand-blue/30',
      pillClass: 'bg-brand-blue text-white',
      color: '#0066FF',
      icon: 'verified',
      status: 'VERIFIED',
    };
  }
  if (s >= 35) {
    return {
      label: 'Emerging Creator',
      badgeClass: 'bg-amber-500/15 text-amber-500 border-amber-500/30',
      pillClass: 'bg-amber-500 text-white',
      color: '#F59E0B',
      icon: 'trending_up',
      status: 'EMERGING',
    };
  }
  return {
    label: 'Low Signal / Bot Risk',
    badgeClass: 'bg-red-500/15 text-red-500 border-red-500/30',
    pillClass: 'bg-red-500 text-white',
    color: '#EF4444',
    icon: 'warning',
    status: 'FLAGGED',
  };
}

export function getSorsaUrl(handle) {
  if (!handle) return 'https://app.sorsa.io';
  return `https://app.sorsa.io/profile/${handle.replace('@', '')}`;
}

export function getTwitterScoreUrl(handle) {
  if (!handle) return 'https://twitterscore.io';
  return `https://twitterscore.io/twitter/${handle.replace('@', '')}/overview/`;
}

export function generateVerificationTweet(handle, challengeCode) {
  const clean = handle.replace('@', '');
  if (!challengeCode) {
    // Fallback if no challenge code yet
    const text = `Verifying my @AdPact identity on GenLayer 🚀 #GenLayer #AdPact`;
    return `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
  }
  const text = `Verifying my AdPact identity: ${challengeCode} #AdPact #GenLayer`;
  return `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
}

// Local storage sync per wallet address
export function loadLocalXProfile(address) {
  if (!address) {
    userXProfile.handle = '';
    userXProfile.score = 75;
    userXProfile.status = 'UNVERIFIED';
    userXProfile.isLinked = false;
    return;
  }
  const key = `adpact_x_profile_${address.toLowerCase()}`;
  try {
    const raw = localStorage.getItem(key);
    if (raw) {
      const data = JSON.parse(raw);
      userXProfile.handle = data.handle || '';
      userXProfile.score = data.score || calculateBaselineScore(data.handle);
      userXProfile.status = data.status || 'VERIFIED';
      userXProfile.reason = data.reason || 'Account linked and verified';
      userXProfile.linkedAt = data.linkedAt || new Date().toISOString();
      userXProfile.isLinked = !!data.handle;
      userXProfile.verifiedViaTweet = !!data.verifiedViaTweet;
      return;
    }
  } catch (e) {
    console.warn('Error reading local X profile:', e);
  }

  // Not yet linked
  userXProfile.handle = '';
  userXProfile.score = 75;
  userXProfile.status = 'UNVERIFIED';
  userXProfile.reason = '';
  userXProfile.linkedAt = '';
  userXProfile.isLinked = false;
  userXProfile.challengeCode = '';
  userXProfile.verifiedViaTweet = false;
}

export function saveLocalXProfile(address, profileData) {
  if (!address) return;
  const key = `adpact_x_profile_${address.toLowerCase()}`;
  const data = {
    handle: profileData.handle.replace('@', ''),
    score: profileData.score || calculateBaselineScore(profileData.handle),
    status: profileData.status || 'VERIFIED',
    reason: profileData.reason || 'Account linked and verified',
    linkedAt: profileData.linkedAt || new Date().toISOString(),
    verifiedViaTweet: !!profileData.verifiedViaTweet,
  };
  localStorage.setItem(key, JSON.stringify(data));
  userXProfile.handle = data.handle;
  userXProfile.score = data.score;
  userXProfile.status = data.status;
  userXProfile.reason = data.reason;
  userXProfile.linkedAt = data.linkedAt;
  userXProfile.isLinked = true;
  userXProfile.verifiedViaTweet = data.verifiedViaTweet;
}

export function unlinkLocalXProfile(address) {
  if (!address) return;
  const key = `adpact_x_profile_${address.toLowerCase()}`;
  localStorage.removeItem(key);
  userXProfile.handle = '';
  userXProfile.score = 75;
  userXProfile.status = 'UNVERIFIED';
  userXProfile.reason = '';
  userXProfile.linkedAt = '';
  userXProfile.isLinked = false;
  userXProfile.challengeCode = '';
  userXProfile.verifiedViaTweet = false;
}

// Generate a cryptographically random alphanumeric challenge code (string of letters & numbers)
export function createRandomChallengeCode() {
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const randHex = Array.from(crypto.getRandomValues(new Uint8Array(4)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('')
      .toUpperCase();
    return `ADPACT-${randHex}`;
  }
  return `ADPACT-${Math.random().toString(36).substring(2, 8).toUpperCase()}`;
}

// Challenge code management
export function savePendingChallenge(address, handle, challengeCode) {
  if (!address) return;
  const key = `adpact_x_challenge_${address.toLowerCase()}`;
  const data = { handle: handle.replace('@', '').toLowerCase(), challengeCode, createdAt: new Date().toISOString() };
  localStorage.setItem(key, JSON.stringify(data));
  userXProfile.challengeCode = challengeCode;
}

export function loadPendingChallenge(address) {
  if (!address) return null;
  const key = `adpact_x_challenge_${address.toLowerCase()}`;
  try {
    const raw = localStorage.getItem(key);
    if (raw) {
      const data = JSON.parse(raw);
      // Validate challenge code format: must be a proper alphanumeric string (at least 6 chars)
      if (data && typeof data.challengeCode === 'string' && data.challengeCode.length >= 6) {
        userXProfile.challengeCode = data.challengeCode;
        return data;
      } else {
        // Discard invalid legacy or single-number codes
        localStorage.removeItem(key);
        userXProfile.challengeCode = '';
      }
    }
  } catch (e) {
    console.warn('Error reading pending challenge:', e);
  }
  return null;
}

export function clearPendingChallenge(address) {
  if (!address) return;
  const key = `adpact_x_challenge_${address.toLowerCase()}`;
  localStorage.removeItem(key);
  userXProfile.challengeCode = '';
}

// Watch connected wallet address to automatically load linked profile
watch(
  () => wagmiState.address,
  (newAddr) => {
    loadLocalXProfile(newAddr);
  },
  { immediate: true }
);
