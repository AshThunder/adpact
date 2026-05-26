<template>
  <div class="wallet-connect">
    <!-- Connecting State -->
    <div v-if="wagmiState.isConnecting">
      <button 
        class="font-button text-button bg-surface-container border border-hairline text-primary px-md py-xs rounded-full flex items-center gap-xs opacity-60 cursor-not-allowed"
        disabled
      >
        <div class="w-3.5 h-3.5 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        Connecting...
      </button>
    </div>

    <!-- Disconnected State -->
    <div v-else-if="!wagmiState.isConnected">
      <button 
        class="font-button text-button bg-primary text-on-primary px-md py-xs rounded-full flex items-center gap-xs hover:opacity-90 transition-opacity"
        @click="handleConnect" 
        id="btn-connect-wallet"
      >
        Connect Wallet
      </button>
    </div>

    <!-- Connected State: address pill + disconnect -->
    <div v-else class="flex items-center gap-xs">
      <div class="flex items-center gap-xs bg-surface-1 border border-hairline px-md py-xs rounded-full">
        <div class="w-1.5 h-1.5 rounded-full bg-report-green flex-shrink-0"></div>
        <span class="font-mono text-mono text-primary" :title="wagmiState.address">
          {{ truncatedAddress }}
        </span>
      </div>
      <button 
        class="text-ink-subtle hover:text-primary transition-colors p-xs rounded-lg flex items-center justify-center"
        @click="handleDisconnect" 
        id="btn-disconnect-wallet"
        title="Disconnect wallet"
      >
        <LogOut :size="14" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { LogOut } from 'lucide-vue-next';
import { wagmiState, connectWallet, disconnectWallet } from '../services/wagmi.js';

const truncatedAddress = computed(() => {
  if (!wagmiState.address) return '';
  return `${wagmiState.address.slice(0, 6)}...${wagmiState.address.slice(-4)}`;
});

async function handleConnect() {
  try {
    await connectWallet();
  } catch (err) {
    console.error('Wallet connection failed:', err);
  }
}

async function handleDisconnect() {
  try {
    await disconnectWallet();
  } catch (err) {
    console.error('Disconnect failed:', err);
  }
}
</script>

<style scoped>
/* All styling via Tailwind utility classes above */
</style>
