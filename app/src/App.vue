<template>
  <div class="app-layout">
    <header class="top-nav">
      <div class="nav-content" style="max-width:1440px; margin:0 auto; padding:0 var(--space-xl);">
        <!-- Brand -->
        <a href="#" class="font-headline text-headline text-primary" style="font-size:22px; font-weight:600; letter-spacing:-0.3px; text-decoration:none; white-space:nowrap; display:flex; align-items:center; gap:8px; flex-shrink:0;">
          <img src="/logo.svg" alt="AdPact Logo" style="height: 32px; width: 32px;" />
          AdPact
        </a>

        <!-- Center Nav Links -->
        <nav class="nav-links hidden md:flex items-center gap-xl h-full">
          <a
            href="#"
            class="nav-link font-body text-body h-full flex items-center"
            :class="!wagmiState.isConnected ? 'text-primary font-medium border-b-2 border-primary' : (currentTab === 'all' ? 'text-primary font-medium border-b-2 border-primary' : 'text-ink-subtle hover:text-primary')"
            style="padding-bottom:2px;"
            @click.prevent="wagmiState.isConnected && (currentTab = 'all')"
          >Marketplace</a>
          <a
            v-if="wagmiState.isConnected"
            href="#"
            class="nav-link font-body text-body h-full flex items-center"
            :class="currentTab === 'my_campaigns' ? 'text-primary font-medium border-b-2 border-primary' : 'text-ink-subtle hover:text-primary'"
            style="padding-bottom:2px;"
            @click.prevent="currentTab = 'my_campaigns'"
          >My Campaigns</a>
          <a
            v-if="wagmiState.isConnected"
            href="#"
            class="nav-link font-body text-body h-full flex items-center"
            :class="currentTab === 'my_applications' ? 'text-primary font-medium border-b-2 border-primary' : 'text-ink-subtle hover:text-primary'"
            style="padding-bottom:2px;"
            @click.prevent="currentTab = 'my_applications'"
          >My Applications</a>
          <a
            v-if="wagmiState.isConnected"
            href="#"
            class="nav-link font-body text-body h-full flex items-center"
            :class="currentTab === 'analytics' ? 'text-primary font-medium border-b-2 border-primary' : 'text-ink-subtle hover:text-primary'"
            style="padding-bottom:2px;"
            @click.prevent="currentTab = 'analytics'"
          >Analytics</a>
          <a
            href="/about.html"
            class="nav-link font-body text-body h-full flex items-center text-ink-subtle hover:text-primary"
            style="padding-bottom:2px;"
          >About</a>
        </nav>

        <!-- Right Actions -->
        <div class="nav-actions">
          <!-- Network Selector -->
          <div class="network-picker-container">
            <Globe :size="14" class="network-globe-icon globe-active" />
            <select 
              v-model="selectedNetwork" 
              @change="onNetworkChange" 
              class="network-select"
              id="select-network"
            >
              <option value="studionet">StudioNet</option>
              <option value="bradbury">Bradbury</option>
            </select>
          </div>

          <!-- Balance Display -->
          <div v-if="wagmiState.isConnected" class="balance-display" id="balance-display">
            <span class="font-mono text-mono text-ink-subtle">
              {{ wagmiState.balance ? parseFloat(wagmiState.balance.formatted).toFixed(2) : '0.00' }} GEN
            </span>
          </div>

          <WalletConnect />

          <!-- Hamburger (mobile only) -->
          <button
            class="hamburger-btn md:hidden"
            @click="mobileMenuOpen = !mobileMenuOpen"
            :aria-expanded="mobileMenuOpen"
            aria-label="Toggle navigation menu"
            id="btn-mobile-menu"
          >
            <span v-if="!mobileMenuOpen" class="material-symbols-outlined text-[26px]">menu</span>
            <span v-else class="material-symbols-outlined text-[26px]">close</span>
          </button>
        </div>
      </div>

      <!-- Mobile Dropdown Menu -->
      <Transition name="mobile-menu">
        <nav v-if="mobileMenuOpen" class="mobile-nav md:hidden" id="mobile-nav-menu">
          <a
            href="#"
            class="mobile-nav-link"
            :class="!wagmiState.isConnected || currentTab === 'all' ? 'mobile-nav-link--active' : ''"
            @click.prevent="currentTab = 'all'; mobileMenuOpen = false"
          >
            <span class="material-symbols-outlined text-[20px]">storefront</span>
            Marketplace
          </a>
          <a
            v-if="wagmiState.isConnected"
            href="#"
            class="mobile-nav-link"
            :class="currentTab === 'my_campaigns' ? 'mobile-nav-link--active' : ''"
            @click.prevent="currentTab = 'my_campaigns'; mobileMenuOpen = false"
          >
            <span class="material-symbols-outlined text-[20px]">folder</span>
            My Campaigns
          </a>
          <a
            v-if="wagmiState.isConnected"
            href="#"
            class="mobile-nav-link"
            :class="currentTab === 'my_applications' ? 'mobile-nav-link--active' : ''"
            @click.prevent="currentTab = 'my_applications'; mobileMenuOpen = false"
          >
            <span class="material-symbols-outlined text-[20px]">assignment_turned_in</span>
            My Applications
          </a>
          <a
            v-if="wagmiState.isConnected"
            href="#"
            class="mobile-nav-link"
            :class="currentTab === 'analytics' ? 'mobile-nav-link--active' : ''"
            @click.prevent="currentTab = 'analytics'; mobileMenuOpen = false"
          >
            <span class="material-symbols-outlined text-[20px]">analytics</span>
            Analytics
          </a>
          <a
            href="/about.html"
            class="mobile-nav-link"
            @click="mobileMenuOpen = false"
          >
            <span class="material-symbols-outlined text-[20px]">info</span>
            About
          </a>
        </nav>
      </Transition>
    </header>

    <!-- Faucet Zero Balance Warning Alert Banner -->
    <div v-if="showFaucetWarning" class="faucet-warning-banner" id="faucet-warning-banner">
      <div class="container warning-banner-content">
        <span style="display:flex; align-items:center; gap:var(--space-xs); font-weight: 500;">
          <AlertTriangle :size="16" style="color:var(--color-brand-orange);" />
          Your {{ selectedNetwork === 'bradbury' ? 'Bradbury Testnet' : 'StudioNet' }} balance is 0 GEN. You need GEN tokens to fund escrows or submit verifications.
        </span>
        <a 
          v-if="selectedNetwork === 'bradbury'"
          href="https://testnet-faucet.genlayer.foundation/" 
          target="_blank" 
          class="btn btn-accent btn-sm text-decoration-none"
        >
          Get Test GEN from Faucet
        </a>
        <a 
          v-else
          href="https://studio.genlayer.com/contracts" 
          target="_blank" 
          class="btn btn-accent btn-sm text-decoration-none"
        >
          Claim StudioNet GEN Tokens
        </a>
      </div>
    </div>

    <main class="main-content">
      <Suspense>
        <template #default>
          <Dashboard v-if="wagmiState.isConnected" :account="wagmiAccount" v-model:activeTab="currentTab" />
          <div v-else class="homepage-landing w-full bg-canvas text-primary">
            <!-- Hero Section -->
            <section class="px-xl md:px-2xl py-section max-w-[1440px] mx-auto flex flex-col md:flex-row items-center gap-xxl">
              <div class="flex-1 space-y-lg text-left">
                <h1 class="font-display-lg text-display-lg text-primary max-w-3xl leading-tight hero-title">
                  Trustless Influencer Sponsorships. Governed by <span class="text-fin-orange">AI Consensus.</span>
                </h1>
                <p class="font-subhead text-body-lg text-ink-subtle max-w-2xl">
                  The world's first decentralized creator marketplace. No middlemen. No disputes. Automated escrows verified by AI.
                </p>
                <div class="flex flex-wrap items-center gap-md pt-sm">
                  <button 
                    @click="triggerConnect" 
                    class="bg-primary text-on-primary px-8 py-4 rounded-full font-button text-body hover:opacity-90 transition-opacity flex items-center gap-2 shadow-md"
                    id="btn-hero-connect"
                  >
                    <span class="material-symbols-outlined text-[20px]">account_balance_wallet</span>
                    Connect Wallet &amp; Explore
                  </button>
                  <a 
                    href="#how-it-works"
                    class="bg-surface-1 border border-hairline text-primary px-8 py-4 rounded-full font-button text-body hover:bg-surface-2 transition-colors flex items-center gap-2 shadow-sm text-decoration-none"
                  >
                    View How It Works
                  </a>
                </div>
              </div>
              <div class="flex-1 relative w-full aspect-square md:aspect-auto md:h-[600px] rounded-2xl overflow-hidden border border-hairline shadow-md hover:shadow-lg transition-shadow">
                <img 
                  alt="A premium, minimal 3D illustration for a decentralized influencer marketplace featuring a sleek, futuristic digital eye or a stylized AI neural node floating in the center." 
                  class="w-full h-full object-cover" 
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuBn9sp30-MPwGJkxW3EDyXBB9ySXYtuG9UOXnZ3BBq8EEjiCEVa6g_kKnoi-COCGyO_xI0gkyS-RQACquniBdYDnjqzjfzYU65lzL4NLCTRwUU5TVOtOWcpWlmOKjevuxTYdHgx8Oho4giUNc_RPcTmUKoWtdZsTJuRPqoXaWYJYiNCJ-UKYBazEG-6xjBxeCzURrQNhEGcoCZyZeh0dPVndKcGe8AY19a8uoqmQX3WOgZ_c6ZsU5pxOTee-JrQqK8H_M3GNdqi2NpU"
                />
              </div>
            </section>
 
            <!-- Metrics Banner -->
            <div class="px-xl md:px-2xl pb-section max-w-[1440px] mx-auto">
              <div class="glass-panel rounded-2xl p-xl flex flex-col md:flex-row justify-around items-center gap-lg text-center shadow-md">
                <div class="space-y-xxs">
                  <p class="font-headline text-headline text-primary" style="font-size: 28px;">100% Secure</p>
                  <p class="font-body text-body text-ink-subtle">Smart Contract Escrow</p>
                </div>
                <div class="hidden md:block w-px h-16 bg-hairline"></div>
                <div class="space-y-xxs">
                  <p class="font-headline text-headline text-primary" style="font-size: 28px;">Zero Agency Fees</p>
                  <p class="font-body text-body text-ink-subtle">Direct Creator Deals</p>
                </div>
                <div class="hidden md:block w-px h-16 bg-hairline"></div>
                <div class="space-y-xxs">
                  <p class="font-headline text-headline text-fin-orange" style="font-size: 28px;">Consensus Settled</p>
                  <p class="font-body text-body text-ink-subtle">AI Network Verification</p>
                </div>
              </div>
            </div>
 
            <!-- Workflow Explainer -->
            <section id="how-it-works" class="px-xl md:px-2xl py-section max-w-[1440px] mx-auto scroll-mt-20">
              <div class="text-center mb-xxl">
                <h2 class="font-display-md text-display-md text-primary mb-md section-title">How it Works</h2>
                <p class="font-body-lg text-body-lg text-ink-subtle max-w-3xl mx-auto">From campaign creation to payout, everything is handled trustlessly on-chain.</p>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-4 gap-xl text-left">
                <div class="bg-surface-1 border border-hairline p-xl rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                  <div class="w-14 h-14 bg-surface-container rounded-full flex items-center justify-center mb-lg text-fin-orange">
                    <span class="material-symbols-outlined text-3xl">add_box</span>
                  </div>
                  <h3 class="font-headline text-headline text-primary mb-sm">Create &amp; Escrow</h3>
                  <p class="font-body text-body text-ink-subtle">Brands set rules, post guidelines, and fund the smart contract upfront.</p>
                </div>
                <div class="bg-surface-1 border border-hairline p-xl rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                  <div class="w-14 h-14 bg-surface-container rounded-full flex items-center justify-center mb-lg text-fin-orange">
                    <span class="material-symbols-outlined text-3xl">campaign</span>
                  </div>
                  <h3 class="font-headline text-headline text-primary mb-sm">Apply &amp; Submit</h3>
                  <p class="font-body text-body text-ink-subtle">Creators apply, get approved, and submit drafts or live post URLs.</p>
                </div>
                <div class="bg-surface-1 border border-hairline p-xl rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                  <div class="w-14 h-14 bg-surface-container rounded-full flex items-center justify-center mb-lg text-fin-orange">
                    <span class="material-symbols-outlined text-3xl">psychology</span>
                  </div>
                  <h3 class="font-headline text-headline text-primary mb-sm">AI Verification</h3>
                  <p class="font-body text-body text-ink-subtle">On-chain nodes analyze the content against the initial brand requirements.</p>
                </div>
                <div class="bg-surface-1 border border-hairline p-xl rounded-2xl shadow-sm hover:shadow-md transition-shadow">
                  <div class="w-14 h-14 bg-surface-container rounded-full flex items-center justify-center mb-lg text-fin-orange">
                    <span class="material-symbols-outlined text-3xl">payments</span>
                  </div>
                  <h3 class="font-headline text-headline text-primary mb-sm">Automated Payout</h3>
                  <p class="font-body text-body text-ink-subtle">Funds are instantly released upon successful verification and retention period.</p>
                </div>
              </div>
            </section>

            <!-- Technical Section: The Consensus Loop -->
            <section class="px-xl md:px-2xl py-section max-w-[1440px] mx-auto flex flex-col md:flex-row items-center gap-xxl text-left">
              <div class="flex-1 w-full relative">
                <div class="bg-surface-1 border border-hairline p-xl rounded-2xl shadow-sm relative overflow-hidden h-[440px] flex items-center justify-center">
                  <div class="absolute inset-0 bg-canvas opacity-50 pointer-events-none"></div>
                  <div class="relative z-10 flex flex-col items-center gap-lg w-full max-w-md">
                    <div class="bg-primary text-on-primary px-xl py-md rounded-xl font-mono text-body w-full text-center shadow-md">
                      Post Submitted (URL)
                    </div>
                    <div class="flex justify-center gap-md w-full">
                      <div class="bg-surface-1 border border-fin-orange rounded-lg p-md flex-1 text-center shadow">Node 1<br/><span class="text-sm text-fin-orange font-medium">LLM Eval</span></div>
                      <div class="bg-surface-1 border border-fin-orange rounded-lg p-md flex-1 text-center shadow">Node 2<br/><span class="text-sm text-fin-orange font-medium">LLM Eval</span></div>
                      <div class="bg-surface-1 border border-fin-orange rounded-lg p-md flex-1 text-center shadow">Node 3<br/><span class="text-sm text-fin-orange font-medium">LLM Eval</span></div>
                      <div class="bg-surface-1 border border-hairline rounded-lg p-md flex-1 text-center opacity-50 hidden sm:block">...</div>
                    </div>
                    <div class="bg-report-green text-on-surface px-xl py-md rounded-xl font-mono text-body w-full text-center shadow-md font-bold">
                      Outcome: MAJORITY_AGREE
                    </div>
                  </div>
                </div>
              </div>
              <div class="flex-1 space-y-lg">
                <h2 class="font-display-md text-display-md text-primary" style="font-size: 48px;">The Consensus Loop</h2>
                <p class="font-body-lg text-body-lg text-ink-subtle">
                  Our decentralized network utilizes independent Validator Nodes. Each node runs advanced LLMs to evaluate the submitted post against the campaign's strict criteria.
                </p>
                <ul class="space-y-md text-ink-muted">
                  <li class="flex items-start gap-md">
                    <span class="material-symbols-outlined text-fin-orange mt-1 text-[24px]">check_circle</span>
                    <span class="font-body text-body text-primary">5 independent nodes evaluate every submission.</span>
                  </li>
                  <li class="flex items-start gap-md">
                    <span class="material-symbols-outlined text-fin-orange mt-1 text-[24px]">check_circle</span>
                    <span class="font-body text-body text-primary">Nodes check for brand mentions, sentiment, and visual guidelines.</span>
                  </li>
                  <li class="flex items-start gap-md">
                    <span class="material-symbols-outlined text-fin-orange mt-1 text-[24px]">check_circle</span>
                    <span class="font-body text-body text-primary">Consensus is reached when a majority agree, triggering the smart contract.</span>
                  </li>
                </ul>
              </div>
            </section>

            <!-- Dual-Audience Value Props -->
            <section class="px-xl md:px-2xl py-section max-w-[1440px] mx-auto text-left">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-xl">
                <div class="bg-surface-1 border border-hairline p-xxl rounded-2xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between h-full">
                  <div>
                    <h3 class="font-display-md text-display-md text-primary mb-lg" style="font-size: 36px;">For Advertisers</h3>
                    <p class="font-body-lg text-body-lg text-ink-subtle mb-xl">
                      Say goodbye to manual tracking and unreliable creators. Secure your budget and ensure brand safety.
                    </p>
                    <ul class="space-y-lg mb-xxl">
                      <li class="flex items-start gap-md">
                        <div class="bg-surface-container rounded-full p-2 mt-1 text-primary"><span class="material-symbols-outlined text-[20px]">shield</span></div>
                        <span class="font-body text-body text-primary"><strong>Escrow Protection:</strong> Funds are only released when criteria are perfectly met.</span>
                      </li>
                      <li class="flex items-start gap-md">
                        <div class="bg-surface-container rounded-full p-2 mt-1 text-primary"><span class="material-symbols-outlined text-[20px]">visibility</span></div>
                        <span class="font-body text-body text-primary"><strong>Automated Scrutiny:</strong> AI rigorously checks every post detail.</span>
                      </li>
                      <li class="flex items-start gap-md">
                        <div class="bg-surface-container rounded-full p-2 mt-1 text-primary"><span class="material-symbols-outlined text-[20px]">block</span></div>
                        <span class="font-body text-body text-primary"><strong>No Post-and-Delete:</strong> Built-in retention periods ensure your ad stays live.</span>
                      </li>
                    </ul>
                  </div>
                  <button @click="triggerConnect" class="bg-surface-container text-primary px-xl py-4 rounded-full font-button text-body w-full hover:bg-hairline transition-colors">Create Campaign</button>
                </div>
                <div class="bg-surface-1 border border-hairline p-xxl rounded-2xl shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between h-full">
                  <div>
                    <h3 class="font-display-md text-display-md text-primary mb-lg" style="font-size: 36px;">For Creators</h3>
                    <p class="font-body-lg text-body-lg text-ink-subtle mb-xl">
                      Focus on creating great content. We ensure you get paid instantly and fairly, without relying on subjective approvals.
                    </p>
                    <ul class="space-y-lg mb-xxl">
                      <li class="flex items-start gap-md">
                        <div class="bg-surface-container rounded-full p-2 mt-1 text-fin-orange"><span class="material-symbols-outlined text-[20px]">monetization_on</span></div>
                        <span class="font-body text-body text-primary"><strong>Guaranteed Payments:</strong> Funds are locked upfront. If you deliver, you get paid.</span>
                      </li>
                      <li class="flex items-start gap-md">
                        <div class="bg-surface-container rounded-full p-2 mt-1 text-fin-orange"><span class="material-symbols-outlined text-[20px]">gavel</span></div>
                        <span class="font-body text-body text-primary"><strong>Objective Verification:</strong> AI evaluates based on clear rules, not advertiser mood.</span>
                      </li>
                      <li class="flex items-start gap-md">
                        <div class="bg-surface-container rounded-full p-2 mt-1 text-fin-orange"><span class="material-symbols-outlined text-[20px]">bolt</span></div>
                        <span class="font-body text-body text-primary"><strong>Instant Settlement:</strong> No waiting for net-30 or net-60 terms.</span>
                      </li>
                    </ul>
                  </div>
                  <button @click="triggerConnect" class="bg-primary text-on-primary px-xl py-4 rounded-full font-button text-body w-full hover:opacity-90 transition-opacity shadow-md">Find Sponsorships</button>
                </div>
              </div>
            </section>

            <!-- Dynamic CTA Footer -->
            <section class="bg-surface-1 border-t border-b border-hairline py-section text-center px-xl">
              <div class="max-w-4xl mx-auto space-y-lg">
                <h2 class="font-display-md text-display-md text-primary" style="font-size: 48px;">Ready to launch your first trustless campaign?</h2>
                <p class="font-body-lg text-body-lg text-ink-subtle">Join the decentralized marketplace and experience the future of creator sponsorships.</p>
                <div class="pt-md">
                  <button @click="triggerConnect" class="bg-fin-orange text-white px-8 py-4 rounded-full font-button text-body hover:opacity-90 transition-opacity flex items-center justify-center gap-2 mx-auto shadow-md" id="btn-bottom-connect">
                    <span class="material-symbols-outlined text-[20px]">account_balance_wallet</span>
                    Connect MetaMask Wallet
                  </button>
                </div>
              </div>
            </section>
          </div>
        </template>
        <template #fallback>
          <div class="flex items-center justify-center" style="height: 60vh; display:flex; align-items:center; justify-content:center;">
            <div class="spinner spinner-lg"></div>
          </div>
        </template>
      </Suspense>
    </main>

    <!-- Beautiful Floating Toast Notifications -->
    <div class="toast-container" id="toast-container">
      <TransitionGroup name="toast">
        <div 
          v-for="toast in toasts" 
          :key="toast.id" 
          class="toast-card card-surface" 
          :class="`toast-${toast.type}`"
        >
          <div class="toast-header">
            <div style="display:flex; align-items:center; gap:var(--space-xs);">
              <Loader v-if="toast.type === 'progress'" class="spinner spinner-brand" :size="16" />
              <CheckCircle v-else-if="toast.type === 'success'" style="color:var(--color-brand-green);" :size="16" />
              <XCircle v-else-if="toast.type === 'error'" style="color:var(--color-brand-red);" :size="16" />
              <Globe v-else style="color:var(--color-slate);" :size="16" />
              <span class="type-body-sm-semibold toast-title">{{ toast.title }}</span>
            </div>
            <button @click="removeToast(toast.id)" class="toast-close-btn">&times;</button>
          </div>
          
          <div class="toast-body">
            <p v-if="toast.message" class="type-body-sm" style="color:var(--color-on-dark-muted); margin-bottom:var(--space-xs); font-size: 13px; line-height: 1.4;">{{ toast.message }}</p>
            
            <!-- Multi-step progress bar -->
            <div v-if="toast.type === 'progress' && toast.steps.length > 0" class="toast-steps">
              <div v-for="(step, idx) in toast.steps" :key="step" class="toast-step" :class="{ 'step-active': idx === toast.currentStep, 'step-completed': idx < toast.currentStep }">
                <div class="step-dot">
                  <CheckCircle v-if="idx < toast.currentStep" :size="10" style="color:var(--color-brand-green);" />
                </div>
                <span class="step-label">{{ step }}</span>
              </div>
            </div>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <footer class="footer-region">
      <div class="container" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:var(--space-md);">
        <div class="type-body-sm" style="color:var(--color-steel);">
          © 2026 AdPact. Powered by GenLayer Decentralized AI Consensus.
        </div>
        <div style="display:flex; gap:var(--space-md);">
          <a href="https://studio.genlayer.com" target="_blank" class="footer-link">GenLayer Studio</a>
          <a v-if="explorerUrl" :href="explorerUrl" target="_blank" class="footer-link">Explorer</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Wallet, Globe, AlertTriangle, CheckCircle, Loader, XCircle } from 'lucide-vue-next';
import WalletConnect from './components/WalletConnect.vue';
import Dashboard from './components/Dashboard.vue';
import { wagmiState, connectWallet } from './services/wagmi.js';
import { selectedNetwork, setNetwork, syncSnapConnection } from './services/genlayer.js';

// Computed account object expected by dashboard & details
const wagmiAccount = computed(() => {
  if (!wagmiState.address) return null;
  return {
    address: wagmiState.address,
  };
});

const currentTab = ref('all');
const mobileMenuOpen = ref(false);

// Faucet warning trigger on 0 balance
const showFaucetWarning = computed(() => {
  return (
    wagmiState.isConnected &&
    wagmiState.balance &&
    parseFloat(wagmiState.balance.formatted) === 0
  );
});

// Floating Toasts State Management
const toasts = ref([]);

function addToast(toast) {
  const id = Date.now() + Math.random().toString(36).substring(2, 9);
  const newToast = {
    id,
    title: toast.title || 'Notification',
    message: toast.message || '',
    type: toast.type || 'info', // 'info', 'success', 'error', 'progress'
    steps: toast.steps || [],
    currentStep: toast.currentStep !== undefined ? toast.currentStep : 0,
    duration: toast.duration || 5000,
  };
  toasts.value.push(newToast);

  if (newToast.type !== 'progress' && newToast.duration > 0) {
    setTimeout(() => {
      removeToast(id);
    }, newToast.duration);
  }
  return id;
}

function updateToast(id, updates) {
  const index = toasts.value.findIndex(t => t.id === id);
  if (index !== -1) {
    toasts.value[index] = { ...toasts.value[index], ...updates };
    // Auto-dismiss if transitioned away from progress to standard warning/success
    if (updates.type && updates.type !== 'progress' && !updates.duration) {
      setTimeout(() => {
        removeToast(id);
      }, 5000);
    }
  }
}

function removeToast(id) {
  toasts.value = toasts.value.filter(t => t.id !== id);
}

// Global exposure
window.marketplaceToast = {
  add: addToast,
  update: updateToast,
  remove: removeToast,
};

// Dynamic explorer URL based on selected network
const explorerUrl = computed(() => {
  if (selectedNetwork.value === 'bradbury') {
    return 'https://explorer-bradbury.genlayer.com';
  } else if (selectedNetwork.value === 'studionet') {
    return 'https://explorer-studio.genlayer.com';
  }
  return null;
});

function onNetworkChange(event) {
  const newNet = event.target.value;
  setNetwork(newNet);
  console.log(`Network switched to: ${newNet}`);
  
  // Re-verify snap connection if already connected to wallet
  if (wagmiState.isConnected) {
    syncSnapConnection().catch(err => {
      console.warn("Failed to automatically sync snap network on select switch:", err);
    });
  }
}

async function triggerConnect() {
  try {
    await connectWallet();
  } catch (err) {
    console.error('MetaMask connection trigger failed:', err);
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-canvas);
}

.top-nav {
  background: var(--color-canvas);
  border-bottom: 1px solid var(--color-hairline);
  position: sticky;
  top: 0;
  z-index: 50;
}

.nav-content {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-xl);
}

.nav-links {
  flex: 1;
}

.nav-link {
  text-decoration: none;
  transition: color 0.15s ease;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.3px;
  color: var(--color-ink);
  text-decoration: none;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

/* ── Hamburger Button ───────────────────────────────────── */
.hamburger-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-sm);
  padding: 4px;
  color: var(--color-ink);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
  flex-shrink: 0;
}
.hamburger-btn:hover {
  background: var(--color-surface);
}

/* ── Mobile Nav Dropdown ────────────────────────────────── */
.mobile-nav {
  background: var(--color-canvas);
  border-top: 1px solid var(--color-hairline);
  border-bottom: 1px solid var(--color-hairline);
  padding: var(--space-sm) 0;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-xl);
  font-size: 15px;
  font-weight: 500;
  color: var(--color-steel);
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: background 0.12s ease, color 0.12s ease, border-color 0.12s ease;
}
.mobile-nav-link:hover {
  background: var(--color-surface);
  color: var(--color-ink);
}
.mobile-nav-link--active {
  color: var(--color-ink);
  border-left-color: var(--color-brand-green);
  background: var(--color-surface-soft);
  font-weight: 600;
}

/* Slide-down transition */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: max-height 0.25s ease, opacity 0.2s ease;
  overflow: hidden;
  max-height: 400px;
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  max-height: 0;
  opacity: 0;
}

.network-picker-container {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  background: var(--color-surface);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-full);
  padding: 4px 12px;
  transition: all 0.2s ease;
}

.network-picker-container:hover {
  border-color: var(--color-hairline-bright);
}

.network-globe-icon {
  color: var(--color-slate);
  transition: color 0.3s ease;
}

.globe-active {
  color: var(--color-brand-green);
  filter: drop-shadow(0 0 4px rgba(0, 212, 164, 0.4));
}

.network-select {
  background: transparent;
  border: none;
  color: var(--color-ink);
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 600;
  outline: none;
  cursor: pointer;
  padding-right: 4px;
}

.network-select option {
  background: var(--color-surface);
  color: var(--color-ink);
}

.balance-display {
  background: var(--color-surface);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-full);
  padding: 5px 14px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-ink);
  display: flex;
  align-items: center;
}

.faucet-warning-banner {
  background: rgba(245, 158, 11, 0.08);
  border-bottom: 1px solid rgba(245, 158, 11, 0.15);
  padding: 10px 0;
  font-size: 13px;
  color: var(--color-ink);
  animation: slideDown 0.3s ease-out;
}

.warning-banner-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.main-content {
  flex: 1;
  background: var(--color-canvas);
  padding-bottom: var(--space-hero);
}

.empty-state-welcome {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 180px);
  padding: var(--space-xl) 0;
}

.welcome-card {
  text-align: center;
  padding: var(--space-xxxl) var(--space-xxl);
  max-width: 600px;
  width: 100%;
  border-radius: var(--rounded-lg);
  box-shadow: var(--shadow-deep);
}

.empty-state-icon-wrapper {
  width: 64px;
  height: 64px;
  background: var(--color-surface-soft);
  border-radius: var(--rounded-full);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto var(--space-xl);
  border: 1px solid var(--color-hairline);
  transition: transform 0.3s ease;
}

.welcome-card:hover .empty-state-icon-wrapper {
  transform: scale(1.05);
}

.welcome-wallet-icon {
  width: 28px;
  height: 28px;
  color: var(--color-brand-green);
}

/* Beautiful Floating Toasts Styles */
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1000;
  max-width: 380px;
  width: calc(100vw - 48px);
}

.toast-card {
  background: rgba(18, 18, 18, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid var(--color-hairline);
  border-radius: var(--rounded-md);
  box-shadow: var(--shadow-deep);
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.toast-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.toast-title {
  color: var(--color-on-dark);
}

.toast-close-btn {
  background: transparent;
  border: none;
  color: var(--color-on-dark-muted);
  cursor: pointer;
  font-size: 18px;
  padding: 0;
  line-height: 1;
  transition: color 0.15s ease;
}

.toast-close-btn:hover {
  color: var(--color-on-dark);
}

.toast-steps {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 10px;
  border-left: 2px solid rgba(255, 255, 255, 0.1);
  padding-left: 14px;
  margin-left: 6px;
}

.toast-step {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  position: relative;
  line-height: 1.2;
}

.toast-step.step-active {
  color: var(--color-brand-green);
  font-weight: 600;
}

.toast-step.step-completed {
  color: rgba(255, 255, 255, 0.85);
}

.step-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  position: absolute;
  left: -20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-step.step-active .step-dot {
  background: var(--color-brand-green);
  box-shadow: 0 0 8px rgba(0, 212, 164, 0.6);
}

.toast-step.step-completed .step-dot {
  background: var(--color-brand-green);
  border: 1px solid var(--color-brand-green);
}

.toast-step.step-completed .step-dot :deep(svg) {
  width: 10px;
  height: 10px;
}

/* Animations */
.toast-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}
.toast-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
  }
  to {
    transform: translateY(0);
  }
}

.footer-region {
  background: var(--color-canvas);
  border-top: 1px solid var(--color-hairline);
  padding: var(--space-xl) 0;
}

.footer-link {
  color: var(--color-slate);
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.15s ease;
}

.footer-link:hover {
  color: var(--color-brand-green);
}

/* ── Mobile Responsive Styles ────────────────────────────── */
.hero-title {
  font-size: 64px;
}
.section-title {
  font-size: 48px;
}

@media (max-width: 991px) {
  .hero-title {
    font-size: 44px;
  }
  .section-title {
    font-size: 36px;
  }
}

@media (max-width: 640px) {
  .hero-title {
    font-size: 32px;
    line-height: 1.2;
  }
  .section-title {
    font-size: 28px;
  }
  .nav-content {
    padding: 0 var(--space-md) !important;
    gap: var(--space-xs) !important;
  }
  .nav-actions {
    gap: 6px !important;
  }
  .balance-display {
    display: none !important; /* Hide balance on small screens to save valuable space */
  }
  .network-picker-container {
    padding: 4px 8px !important;
  }
  .network-select {
    font-size: 11px !important;
  }
  .faucet-warning-banner {
    padding: 12px 16px !important;
    font-size: 12px !important;
  }
  .warning-banner-content {
    flex-direction: column !important;
    align-items: stretch !important;
    text-align: center;
  }
}
</style>

