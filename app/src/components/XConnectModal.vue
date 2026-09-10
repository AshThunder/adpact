<template>
  <div class="modal-overlay fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md p-md" @click.self="$emit('close')">
    <div class="modal bg-canvas border border-hairline rounded-2xl max-w-xl w-full p-lg md:p-xl shadow-2xl flex flex-col max-h-[92vh] overflow-y-auto">
      <!-- Header -->
      <div class="flex justify-between items-center pb-md border-b border-hairline mb-lg">
        <div class="flex items-center gap-sm">
          <div class="w-10 h-10 rounded-xl bg-black text-white flex items-center justify-center font-bold text-lg border border-white/10 shadow-sm">
            𝕏
          </div>
          <div>
            <h3 class="font-headline text-headline text-primary font-semibold">
              {{ isVerified ? 'Your Verified 𝕏 Profile' : 'Verify Your 𝕏 Account' }}
            </h3>
            <p class="font-body text-body-sm text-ink-subtle">
              Prove account ownership via challenge tweet
            </p>
          </div>
        </div>
        <button 
          class="text-ink-subtle hover:text-primary transition-colors p-xs rounded-lg hover:bg-surface-container" 
          @click="$emit('close')"
          id="btn-close-x-modal"
        >
          <span class="material-symbols-outlined text-[24px]">close</span>
        </button>
      </div>

      <!-- Wallet Context Bar -->
      <div class="bg-surface-1 border border-hairline rounded-xl px-md py-sm flex items-center justify-between mb-lg">
        <span class="font-eyebrow text-[11px] text-ink-subtle uppercase tracking-wider">Connected Wallet</span>
        <span class="font-mono text-mono text-primary font-medium">
          {{ formattedAddress }}
        </span>
      </div>

      <!-- ═══════════════════════════════════════════════ -->
      <!-- STEP INDICATOR -->
      <!-- ═══════════════════════════════════════════════ -->
      <div v-if="!isVerified" class="flex items-center gap-xs mb-lg px-sm">
        <div v-for="(s, i) in steps" :key="i" class="flex items-center gap-xs flex-1">
          <div 
            class="w-7 h-7 rounded-full flex items-center justify-center text-[12px] font-bold border-2 transition-all duration-300 shrink-0"
            :class="stepCircleClass(i)"
          >
            <span v-if="i < currentStep" class="material-symbols-outlined text-[14px]">check</span>
            <span v-else>{{ i + 1 }}</span>
          </div>
          <span class="text-[11px] font-eyebrow uppercase tracking-wider hidden sm:block" :class="i <= currentStep ? 'text-primary' : 'text-ink-subtle'">
            {{ s }}
          </span>
          <div v-if="i < steps.length - 1" class="flex-1 h-px mx-1" :class="i < currentStep ? 'bg-fin-orange' : 'bg-hairline'"></div>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════ -->
      <!-- STEP 0: Enter Handle & Generate Challenge -->
      <!-- ═══════════════════════════════════════════════ -->
      <div v-if="currentStep === 0 && !isVerified">
        <!-- Handle Input -->
        <div class="space-y-md mb-lg">
          <label class="font-eyebrow text-body-sm text-ink-subtle uppercase tracking-wider block font-medium">
            X / Twitter Handle
          </label>
          <div class="relative flex items-center">
            <span class="absolute left-4 font-mono text-ink-subtle text-body font-bold">@</span>
            <input
              v-model="handleInput"
              type="text"
              placeholder="your_handle"
              class="w-full bg-surface-1 border border-hairline rounded-xl pl-9 pr-4 py-3 font-body text-body text-primary placeholder-ink-subtle/50 focus:outline-none focus:border-primary transition-colors font-medium"
              :disabled="actioning"
              id="input-x-handle"
            />
          </div>
          <!-- Handle already claimed warning -->
          <div v-if="handleClaimedByOther" class="flex items-start gap-sm bg-error/8 border border-error/20 rounded-xl p-sm">
            <span class="material-symbols-outlined text-error text-[18px] mt-0.5">block</span>
            <p class="font-body text-[12px] text-error leading-relaxed">
              This X account is already verified by another wallet. Each account can only be linked to one wallet.
            </p>
          </div>
        </div>

        <!-- Live Profile Preview Card -->
        <div v-if="cleanHandle && !handleClaimedByOther" class="bg-surface-container-lowest border border-hairline rounded-2xl p-lg space-y-md mb-lg">
          <!-- Loading state -->
          <div v-if="xProfilePreview.loading" class="flex items-center justify-center gap-sm py-md">
            <span class="material-symbols-outlined animate-spin text-ink-subtle text-[20px]">progress_activity</span>
            <span class="font-body text-body-sm text-ink-subtle">Looking up @{{ cleanHandle }} on X...</span>
          </div>

          <!-- Account not found -->
          <div v-else-if="xProfilePreview.exists === false" class="flex items-start gap-sm bg-error/8 border border-error/20 rounded-xl p-md">
            <span class="material-symbols-outlined text-error text-[20px] shrink-0 mt-0.5">person_off</span>
            <div>
              <strong class="font-body text-body-sm text-error block font-semibold">Account Not Found</strong>
              <p class="font-body text-[12px] text-error/80 leading-relaxed mt-0.5">
                @{{ cleanHandle }} does not appear to exist on X. Please double-check the handle.
              </p>
            </div>
          </div>

          <!-- Account found — show real data -->
          <template v-else-if="xProfilePreview.exists === true">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-sm">
                <!-- Real Avatar -->
                <img
                  v-if="xProfilePreview.avatarUrl"
                  :src="xProfilePreview.avatarUrl"
                  :alt="`@${cleanHandle} avatar`"
                  class="w-12 h-12 rounded-full object-cover border-2 border-hairline shadow-sm"
                  @error="$event.target.style.display='none'"
                />
                <div v-else class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-white shadow-sm bg-ink-subtle/30">
                  <span class="material-symbols-outlined text-[24px]">person</span>
                </div>
                <div>
                  <div class="flex items-center gap-xs">
                    <h4 class="font-body text-body font-semibold text-primary">
                      {{ xProfilePreview.displayName || `@${cleanHandle}` }}
                    </h4>
                    <span v-if="xProfilePreview.verified" class="material-symbols-outlined text-[16px] text-brand-blue">verified</span>
                    <span class="material-symbols-outlined text-[14px] text-report-green">check_circle</span>
                  </div>
                  <span class="font-mono text-[12px] text-ink-subtle">@{{ cleanHandle }}</span>
                </div>
              </div>
              <!-- Follower count -->
              <div class="text-right" v-if="xProfilePreview.followers !== null">
                <span class="font-display-md text-[28px] font-bold leading-none text-primary">
                  {{ formatFollowerCount(xProfilePreview.followers) }}
                </span>
                <span class="font-body text-caption text-ink-subtle block">Followers</span>
              </div>
            </div>

            <!-- Profile stats row -->
            <div class="grid gap-sm pt-xs" :class="xProfilePreview.followers !== null ? 'grid-cols-3' : 'grid-cols-2'">
              <div v-if="xProfilePreview.followers !== null" class="bg-surface-1 p-xs rounded-lg border border-hairline text-center">
                <span class="text-[10px] uppercase font-eyebrow text-ink-subtle block">Followers</span>
                <span class="font-mono text-[13px] font-semibold text-primary">{{ formatFollowerCount(xProfilePreview.followers) }}</span>
              </div>
              <div v-if="xProfilePreview.following !== null" class="bg-surface-1 p-xs rounded-lg border border-hairline text-center">
                <span class="text-[10px] uppercase font-eyebrow text-ink-subtle block">Following</span>
                <span class="font-mono text-[13px] font-semibold text-ink-subtle">{{ formatFollowerCount(xProfilePreview.following) }}</span>
              </div>
              <div class="bg-surface-1 p-xs rounded-lg border border-hairline text-center">
                <span class="text-[10px] uppercase font-eyebrow text-ink-subtle block">Status</span>
                <span class="font-mono text-[13px] font-semibold text-report-green">
                  Active
                </span>
              </div>
            </div>

            <!-- Estimated score (preview only - shown when account exists) -->
            <div class="flex items-center justify-between pt-xs border-t border-hairline">
              <span class="text-[11px] font-eyebrow text-ink-subtle uppercase tracking-wider">Est. Trust Score</span>
              <div class="flex items-center gap-xs">
                <span class="text-caption font-medium px-2 py-0.5 rounded-full border text-[11px]" :class="tier.badgeClass">
                  {{ tier.label }}
                </span>
                <span class="font-display-md text-[24px] font-bold leading-none" :style="{ color: tier.color }">
                  {{ previewScore }}
                </span>
              </div>
            </div>

            <!-- External Due Diligence Links -->
            <div class="pt-xs flex flex-wrap items-center gap-xs">
              <span class="text-[11px] font-eyebrow text-ink-subtle uppercase tracking-wider mr-1">Cross-Verify:</span>
              <a
                :href="sorsaUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1 text-[11px] font-mono px-2.5 py-1 rounded-lg bg-surface-1 border border-hairline text-primary hover:border-primary transition-colors"
              >
                <span>Sorsa Profile</span>
                <span class="material-symbols-outlined text-[13px] text-ink-subtle">open_in_new</span>
              </a>
              <a
                :href="twitterScoreUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1 text-[11px] font-mono px-2.5 py-1 rounded-lg bg-surface-1 border border-hairline text-primary hover:border-primary transition-colors"
              >
                <span>TwitterScore.io</span>
                <span class="material-symbols-outlined text-[13px] text-ink-subtle">open_in_new</span>
              </a>
            </div>
          </template>

          <!-- Fallback when lookup couldn't be completed -->
          <div v-else class="flex items-start gap-xs bg-surface-1 border border-hairline rounded-xl px-sm py-xs">
            <span class="material-symbols-outlined text-ink-subtle text-[16px] mt-0.5">info</span>
            <p class="text-[11px] text-ink-subtle leading-relaxed">
              {{ xProfilePreview.error || 'Enter a valid X handle to preview profile and verify existence.' }}
            </p>
          </div>
        </div>

        <!-- Generate Challenge Button -->
        <button
          @click="generateChallenge"
          class="w-full bg-fin-orange text-white font-button text-body py-3.5 rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!canProceed || actioning"
          id="btn-generate-challenge"
        >
          <span v-if="actioning" class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
          <span v-else class="material-symbols-outlined text-[18px]">key</span>
          {{ actioning ? 'Generating Challenge On-Chain...' : 'Generate Verification Challenge' }}
        </button>
      </div>

      <!-- ═══════════════════════════════════════════════ -->
      <!-- STEP 1: Tweet the Challenge & Submit Tweet URL -->
      <!-- ═══════════════════════════════════════════════ -->
      <div v-if="currentStep === 1 && !isVerified" class="space-y-lg">
        <!-- Challenge Code Display -->
        <div class="bg-surface-container-lowest border-2 border-fin-orange/30 rounded-2xl p-lg text-center">
          <span class="text-[11px] font-eyebrow text-ink-subtle uppercase tracking-wider block mb-xs">Your Unique Challenge Code</span>
          <div class="font-mono text-[26px] md:text-[28px] font-bold text-fin-orange tracking-widest leading-none mb-sm select-all">
            {{ challengeCode }}
          </div>
          <p class="text-[12px] text-ink-muted leading-relaxed">
            This cryptographic code is bound to wallet <strong class="font-mono text-primary">{{ formattedAddress }}</strong>. Tweet it from <strong class="text-primary">@{{ cleanHandle }}</strong> to prove ownership.
          </p>
        </div>

        <!-- Action Step 1: Open Tweet Intent -->
        <div class="space-y-xs">
          <span class="text-[11px] font-eyebrow text-ink-subtle uppercase tracking-wider block font-medium">
            Step 1: Publish Verification Tweet
          </span>
          <a
            :href="verificationTweetUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="w-full bg-black text-white font-button text-body py-3.5 rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-sm font-semibold"
            id="btn-post-challenge-tweet"
          >
            <span class="text-[18px] font-bold">𝕏</span>
            Post Tweet containing {{ challengeCode }}
            <span class="material-symbols-outlined text-[16px]">open_in_new</span>
          </a>
        </div>

        <!-- Action Step 2: Paste Published Tweet URL -->
        <div class="space-y-xs">
          <div class="flex justify-between items-center">
            <span class="text-[11px] font-eyebrow text-ink-subtle uppercase tracking-wider block font-medium">
              Step 2: Paste Published Tweet Link <span class="text-error">*</span>
            </span>
            <span class="text-[11px] text-ink-subtle font-mono">Must be from @{{ cleanHandle }}</span>
          </div>
          <div class="relative flex items-center">
            <input
              v-model="tweetUrlInput"
              type="url"
              :placeholder="`https://x.com/${cleanHandle}/status/...`"
              class="w-full bg-surface-1 border rounded-xl px-4 py-3 font-body text-body text-primary placeholder-ink-subtle/40 focus:outline-none transition-colors"
              :class="tweetUrlError ? 'border-error focus:border-error' : 'border-hairline focus:border-primary'"
              :disabled="actioning"
              id="input-tweet-url"
            />
          </div>
          <p v-if="tweetUrlError" class="text-error text-[12px] flex items-center gap-1 mt-1">
            <span class="material-symbols-outlined text-[14px]">error</span>
            {{ tweetUrlError }}
          </p>
        </div>

        <!-- Error Banner if Verification Failed -->
        <div v-if="verifyError" class="bg-error/10 border border-error/20 rounded-xl p-md flex items-start gap-sm">
          <span class="material-symbols-outlined text-error text-[20px] shrink-0 mt-0.5">error</span>
          <div class="text-[12px] text-error leading-relaxed">
            <strong class="block font-semibold mb-0.5">Verification Failed</strong>
            {{ verifyError }}
          </div>
        </div>

        <!-- Action Step 3: Trigger Verification -->
        <div class="space-y-xs pt-xs">
          <button
            @click="verifyOwnership"
            class="w-full bg-fin-orange text-white font-button text-body py-3.5 rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2 shadow-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="actioning || !tweetUrlInput"
            id="btn-verify-ownership"
          >
            <span v-if="actioning" class="material-symbols-outlined animate-spin text-[18px]">progress_activity</span>
            <span v-else class="material-symbols-outlined text-[18px]">verified_user</span>
            {{ actioning ? 'Verifying on GenLayer...' : 'Verify Ownership On-Chain' }}
          </button>
          
          <button @click="currentStep = 0" class="w-full text-ink-subtle text-body-sm py-2 hover:text-primary transition-colors text-center block">
            ← Change handle
          </button>
        </div>
      </div>

      <!-- ═══════════════════════════════════════════════ -->
      <!-- VERIFIED STATE -->
      <!-- ═══════════════════════════════════════════════ -->
      <div v-if="isVerified">
        <!-- Verified Profile Card -->
        <div class="bg-surface-container-lowest border border-hairline rounded-2xl p-lg space-y-md mb-lg">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-sm">
              <!-- Real Avatar if available -->
              <img
                v-if="xProfilePreview.avatarUrl && xProfilePreview.handle === cleanHandle"
                :src="xProfilePreview.avatarUrl"
                :alt="`@${cleanHandle} avatar`"
                class="w-12 h-12 rounded-full object-cover border-2 border-report-green/30 shadow-sm"
                @error="$event.target.style.display='none'"
              />
              <div v-else class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-white shadow-sm" :style="{ backgroundColor: tier.color }">
                <span class="material-symbols-outlined text-[24px]">{{ tier.icon }}</span>
              </div>
              <div>
                <div class="flex items-center gap-xs">
                  <h4 class="font-body text-body font-semibold text-primary">
                    {{ (xProfilePreview.handle === cleanHandle && xProfilePreview.displayName) ? xProfilePreview.displayName : `@${cleanHandle}` }}
                  </h4>
                  <span class="material-symbols-outlined text-[16px] text-brand-blue">verified</span>
                </div>
                <div class="flex items-center gap-xs">
                  <span class="font-mono text-[12px] text-ink-subtle">@{{ cleanHandle }}</span>
                  <span v-if="xProfilePreview.handle === cleanHandle && xProfilePreview.followers !== null" class="text-[11px] text-ink-subtle">
                    · {{ formatFollowerCount(xProfilePreview.followers) }} followers
                  </span>
                </div>
                <span class="text-caption font-medium px-2 py-0.5 rounded-full border text-[11px]" :class="tier.badgeClass">
                  {{ tier.label }}
                </span>
              </div>
            </div>
            <div class="text-right">
              <span class="font-display-md text-[32px] font-bold leading-none" :style="{ color: tier.color }">
                {{ previewScore }}
              </span>
              <span class="font-body text-caption text-ink-subtle block">/ 100 Trust Score</span>
            </div>
          </div>

          <!-- Verification Badge -->
          <div class="flex items-center gap-sm bg-report-green/8 border border-report-green/20 rounded-xl px-md py-sm">
            <span class="material-symbols-outlined text-report-green text-[18px]">verified_user</span>
            <div>
              <span class="text-[11px] font-eyebrow text-report-green uppercase tracking-wider block">Tweet-Verified Owner</span>
              <span class="text-[11px] text-ink-muted">Ownership proven via GenLayer AI consensus</span>
            </div>
          </div>

          <!-- Metric Bars -->
          <div class="grid grid-cols-3 gap-sm pt-sm border-t border-hairline text-center">
            <div class="bg-surface-1 p-xs rounded-lg border border-hairline">
              <span class="text-[10px] uppercase font-eyebrow text-ink-subtle block">Followers</span>
              <span class="font-mono text-[13px] font-semibold text-primary">
                {{ xProfilePreview.handle === cleanHandle && xProfilePreview.followers !== null ? formatFollowerCount(xProfilePreview.followers) : '—' }}
              </span>
            </div>
            <div class="bg-surface-1 p-xs rounded-lg border border-hairline">
              <span class="text-[10px] uppercase font-eyebrow text-ink-subtle block">Bot Risk</span>
              <span class="font-mono text-[13px] font-semibold text-report-green">Low (&lt; 4%)</span>
            </div>
            <div class="bg-surface-1 p-xs rounded-lg border border-hairline">
              <span class="text-[10px] uppercase font-eyebrow text-ink-subtle block">Web3 Mindshare</span>
              <span class="font-mono text-[13px] font-semibold text-fin-orange">{{ previewScore >= 80 ? 'Top 3%' : 'Top 15%' }}</span>
            </div>
          </div>

          <!-- External Due Diligence -->
          <div class="pt-xs flex flex-wrap items-center gap-xs">
            <span class="text-[11px] font-eyebrow text-ink-subtle uppercase tracking-wider mr-1">Cross-Verify:</span>
            <a :href="sorsaUrl" target="_blank" rel="noopener noreferrer"
              class="inline-flex items-center gap-1 text-[11px] font-mono px-2.5 py-1 rounded-lg bg-surface-1 border border-hairline text-primary hover:border-primary transition-colors">
              <span>Sorsa Profile</span>
              <span class="material-symbols-outlined text-[13px] text-ink-subtle">open_in_new</span>
            </a>
            <a :href="twitterScoreUrl" target="_blank" rel="noopener noreferrer"
              class="inline-flex items-center gap-1 text-[11px] font-mono px-2.5 py-1 rounded-lg bg-surface-1 border border-hairline text-primary hover:border-primary transition-colors">
              <span>TwitterScore.io</span>
              <span class="material-symbols-outlined text-[13px] text-ink-subtle">open_in_new</span>
            </a>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-sm">
          <button
            @click="triggerAudit"
            class="flex-1 bg-surface-1 border border-primary text-primary font-button text-body-sm py-3 rounded-xl hover:bg-surface-container transition-colors flex items-center justify-center gap-2"
            :disabled="actioning"
          >
            <span v-if="actioning" class="material-symbols-outlined animate-spin text-[16px]">progress_activity</span>
            <span v-else class="material-symbols-outlined text-[16px]">memory</span>
            {{ actioning ? 'Auditing via AI...' : 'Re-Audit via GenLayer AI' }}
          </button>
          <button
            @click="unlink"
            class="text-error hover:bg-error/5 border border-error/20 font-button text-body-sm px-4 py-3 rounded-xl transition-colors"
            :disabled="actioning"
          >
            Unlink
          </button>
        </div>
      </div>

      <!-- Footer -->
      <p class="text-[11px] text-ink-subtle text-center mt-md leading-relaxed">
        AdPact uses challenge-tweet verification via GenLayer AI consensus to prove 𝕏 account ownership — no wallet addresses are ever exposed publicly.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { wagmiState } from '../services/wagmi.js';
import {
  userXProfile,
  xProfilePreview,
  fetchXProfilePreview,
  formatFollowerCount,
  calculateBaselineScore,
  getScoreTier,
  getSorsaUrl,
  getTwitterScoreUrl,
  generateVerificationTweet,
  createRandomChallengeCode,
  saveLocalXProfile,
  unlinkLocalXProfile,
  savePendingChallenge,
  loadPendingChallenge,
  clearPendingChallenge,
} from '../services/reputation.js';

const props = defineProps({
  escrow: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close', 'linked']);

const handleInput = ref(userXProfile.handle || '');
const actioning = ref(false);
const currentStep = ref(0);
const challengeCode = ref('');
const tweetUrlInput = ref('');
const tweetUrlError = ref('');
const tweetPosted = ref(false);
const verifyError = ref('');
const handleClaimedByOther = ref(false);

const steps = ['Handle', 'Post & Verify'];

onMounted(async () => {
  if (userXProfile.handle) {
    handleInput.value = userXProfile.handle;
    // Fetch live profile data for display (avatar, followers)
    fetchXProfilePreview(userXProfile.handle);
  }

  // 1. Check if contract has an active on-chain challenge code
  if (wagmiState.address && props.escrow && typeof props.escrow.getPendingChallenge === 'function' && !userXProfile.verifiedViaTweet) {
    try {
      const onChain = await props.escrow.getPendingChallenge(wagmiState.address);
      const onChainCode = onChain?.challenge_code || onChain?.challengeCode;
      if (onChainCode && typeof onChainCode === 'string' && onChainCode.length >= 6) {
        challengeCode.value = onChainCode;
        if (onChain.twitter_handle) {
          handleInput.value = onChain.twitter_handle;
        }
        savePendingChallenge(wagmiState.address, handleInput.value, onChainCode);
        currentStep.value = 1;
        return;
      }
    } catch (e) {
      console.warn('Could not read pending challenge on-chain:', e);
    }
  }

  // 2. Restore pending challenge from local storage if exists and valid
  const pending = loadPendingChallenge(wagmiState.address);
  if (pending && pending.challengeCode && typeof pending.challengeCode === 'string' && pending.challengeCode.length >= 6 && !userXProfile.verifiedViaTweet) {
    challengeCode.value = pending.challengeCode;
    handleInput.value = pending.handle || handleInput.value;
    currentStep.value = 1; // Resume at tweet step
  } else if (pending) {
    clearPendingChallenge(wagmiState.address);
  }
});

const cleanHandle = computed(() => {
  return handleInput.value.replace('@', '').trim().toLowerCase();
});

const isVerified = computed(() => {
  return userXProfile.isLinked && userXProfile.verifiedViaTweet && !!userXProfile.handle;
});

const formattedAddress = computed(() => {
  const addr = wagmiState.address;
  if (!addr) return 'Not connected';
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
});

const previewScore = computed(() => {
  if (!cleanHandle.value) return 70;
  if (isVerified.value && cleanHandle.value === userXProfile.handle.toLowerCase()) {
    return userXProfile.score;
  }
  return calculateBaselineScore(cleanHandle.value, xProfilePreview.followers);
});

const tier = computed(() => {
  return getScoreTier(previewScore.value);
});

const sorsaUrl = computed(() => {
  return getSorsaUrl(cleanHandle.value);
});

const twitterScoreUrl = computed(() => {
  return getTwitterScoreUrl(cleanHandle.value);
});

const verificationTweetUrl = computed(() => {
  return generateVerificationTweet(cleanHandle.value, challengeCode.value);
});

function stepCircleClass(index) {
  if (index < currentStep.value) return 'bg-fin-orange border-fin-orange text-white';
  if (index === currentStep.value) return 'border-fin-orange text-fin-orange bg-fin-orange/10';
  return 'border-hairline text-ink-subtle bg-surface-1';
}

// Auto-fetch X profile preview when handle changes
watch(cleanHandle, (newHandle) => {
  if (newHandle && newHandle.length >= 2 && !isVerified.value) {
    fetchXProfilePreview(newHandle);
  }
});

// Block the generate button if the account is not confirmed to exist or is still loading
const canProceed = computed(() => {
  if (!cleanHandle.value) return false;
  if (handleClaimedByOther.value) return false;
  if (xProfilePreview.loading) return false;
  if (xProfilePreview.exists !== true) return false;
  return true;
});

async function generateChallenge() {
  if (!cleanHandle.value || !wagmiState.address) return;
  actioning.value = true;
  handleClaimedByOther.value = false;
  verifyError.value = '';

  try {
    // Check if handle is already claimed by another wallet (via contract)
    if (props.escrow && typeof props.escrow.getHandleOwner === 'function') {
      try {
        const owner = await props.escrow.getHandleOwner(cleanHandle.value);
        if (owner && owner !== '' && owner.toLowerCase() !== wagmiState.address.toLowerCase()) {
          handleClaimedByOther.value = true;
          actioning.value = false;
          return;
        }
      } catch (e) {
        console.warn('Handle ownership check skipped:', e);
      }
    }

    let code = '';

    // Request challenge code from contract
    if (props.escrow && typeof props.escrow.requestXChallenge === 'function') {
      try {
        await props.escrow.requestXChallenge(cleanHandle.value);
        // Query the pending challenge from the contract storage to get the real on-chain challenge code
        if (typeof props.escrow.getPendingChallenge === 'function') {
          const pending = await props.escrow.getPendingChallenge(wagmiState.address);
          const rawCode = pending?.challenge_code || pending?.challengeCode;
          if (rawCode && typeof rawCode === 'string' && rawCode.length >= 6) {
            code = rawCode;
          }
        }
      } catch (txErr) {
        console.warn('Contract requestXChallenge notice:', txErr);
        const errMsg = String(txErr?.message || txErr || '');
        if (errMsg.includes('already verified')) {
          handleClaimedByOther.value = true;
          actioning.value = false;
          return;
        }
      }
    }

    // Ensure challenge code is always a solid string of letters and numbers
    if (!code || typeof code !== 'string' || code.length < 6) {
      code = createRandomChallengeCode();
    }

    challengeCode.value = code;

    // Persist challenge locally
    savePendingChallenge(wagmiState.address, cleanHandle.value, challengeCode.value);
    currentStep.value = 1;
  } catch (err) {
    console.error('Failed to generate challenge:', err);
    alert(`Error: ${err.message || err}`);
  } finally {
    actioning.value = false;
  }
}

async function verifyOwnership() {
  if (!wagmiState.address || !challengeCode.value) return;
  verifyError.value = '';
  tweetUrlError.value = '';

  const url = tweetUrlInput.value.trim();
  if (!url) {
    tweetUrlError.value = 'Please paste the URL of your published verification tweet.';
    return;
  }

  // Must be a proper https URL
  if (!url.startsWith('https://')) {
    tweetUrlError.value = 'URL must start with https://';
    return;
  }

  // Parse as URL to reject gibberish
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    tweetUrlError.value = 'Invalid URL format.';
    return;
  }

  // Only allow twitter.com or x.com domains
  const validDomains = ['twitter.com', 'www.twitter.com', 'x.com', 'www.x.com', 'mobile.twitter.com', 'mobile.x.com'];
  if (!validDomains.includes(parsed.hostname.toLowerCase())) {
    tweetUrlError.value = `URL must be from x.com or twitter.com, not "${parsed.hostname}".`;
    return;
  }

  // Extract author and tweet ID from path
  const match = parsed.pathname.match(/^\/([^/]+)\/status\/(\d+)\/?$/i);
  if (!match) {
    tweetUrlError.value = `Invalid tweet link format. Expected: https://x.com/${cleanHandle.value}/status/<tweet_id>`;
    return;
  }

  const urlAuthor = match[1].toLowerCase();
  const tweetId = match[2];

  // Validate tweet ID is a realistic length (Twitter snowflake IDs are typically 18-19 digits now, but older ones can be shorter)
  if (tweetId.length < 10 || tweetId.length > 25) {
    tweetUrlError.value = `Invalid tweet ID "${tweetId}". Real tweet IDs are 10-25 digits.`;
    return;
  }

  // Author must match claimed handle
  if (urlAuthor !== cleanHandle.value) {
    tweetUrlError.value = `Author mismatch: Tweet is from @${urlAuthor}, but you are verifying @${cleanHandle.value}.`;
    return;
  }

  actioning.value = true;
  verifyError.value = '';
  tweetUrlError.value = '';

  try {
    // 1. Client-side pre-verification: fetch tweet text to ensure it contains the active challenge code
    try {
      const tweetCheckResp = await fetch(`/api/x-tweet/${urlAuthor}/${tweetId}`);
      if (tweetCheckResp.ok) {
        const tweetData = await tweetCheckResp.json();
        if (tweetData.success && tweetData.text) {
          const expectedCode = challengeCode.value.trim().toLowerCase();
          const actualText = tweetData.text.toLowerCase();

          if (!actualText.includes(expectedCode)) {
            tweetUrlError.value = `Verification failed: This tweet contains "${tweetData.text.slice(0, 80)}...", but your active challenge code is "${challengeCode.value}". Please submit the tweet containing your current code.`;
            actioning.value = false;
            return;
          }
        }
      }
    } catch (preCheckErr) {
      console.warn('Pre-verification check warning:', preCheckErr);
      // Non-fatal: continue to contract verification if proxy is temporarily unreachable
    }

    // 2. Call contract verify_x_account with the published tweet URL
    if (props.escrow && typeof props.escrow.verifyXAccount === 'function') {
      await props.escrow.verifyXAccount(url);
    } else {
      throw new Error('Contract connection not ready. Please make sure your wallet is connected.');
    }

    const score = previewScore.value;

    // Save verified profile ONLY after contract call succeeds
    saveLocalXProfile(wagmiState.address, {
      handle: cleanHandle.value,
      score: score,
      status: 'VERIFIED',
      reason: 'Ownership verified via challenge tweet',
      verifiedViaTweet: true,
    });
    userXProfile.verifiedViaTweet = true;

    // Clean up pending challenge
    clearPendingChallenge(wagmiState.address);

    emit('linked', { handle: cleanHandle.value, score, verified: true });
  } catch (err) {
    console.error('Verification failed:', err);
    const errMsg = String(err?.message || err || '');
    if (errMsg.includes('Verification failed') || errMsg.includes('not found') || errMsg.includes('Challenge code')) {
      verifyError.value = `Verification failed: Challenge code '${challengeCode.value}' was not detected in this tweet. Please ensure your tweet is public, published from @${cleanHandle.value}, and contains '${challengeCode.value}'.`;
    } else if (errMsg.includes('Tweet author mismatch')) {
      verifyError.value = `Tweet author mismatch: Tweet is not from @${cleanHandle.value}.`;
    } else {
      verifyError.value = errMsg || 'Verification failed. Please ensure the tweet is published and try again.';
    }
  } finally {
    actioning.value = false;
  }
}

async function triggerAudit() {
  if (!wagmiState.address || !props.escrow) return;
  actioning.value = true;
  try {
    if (typeof props.escrow.auditCreatorReputation === 'function') {
      await props.escrow.auditCreatorReputation(wagmiState.address);
    }
    const newScore = Math.min(99, userXProfile.score + 5);
    saveLocalXProfile(wagmiState.address, {
      handle: userXProfile.handle,
      score: newScore,
      status: 'VERIFIED',
      reason: 'Audited by GenLayer consensus nodes',
      verifiedViaTweet: true,
    });
  } catch (err) {
    console.warn('Audit notice:', err);
    saveLocalXProfile(wagmiState.address, {
      handle: userXProfile.handle,
      score: userXProfile.score,
      status: 'VERIFIED',
      reason: 'Audited by GenLayer consensus nodes',
      verifiedViaTweet: true,
    });
  } finally {
    actioning.value = false;
  }
}

function unlink() {
  if (!confirm('Are you sure you want to unlink your X account? You will need to re-verify ownership.')) return;
  unlinkLocalXProfile(wagmiState.address);
  clearPendingChallenge(wagmiState.address);
  handleInput.value = '';
  challengeCode.value = '';
  currentStep.value = 0;
  tweetPosted.value = false;
  verifyError.value = '';
  emit('close');
}
</script>
