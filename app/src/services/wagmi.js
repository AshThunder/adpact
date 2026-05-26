import { ref, readonly } from 'vue';
import { createConfig, http, connect, disconnect, getAccount, watchAccount, reconnect, getBalance } from '@wagmi/core';
import { injected } from '@wagmi/connectors';
import { createClient } from 'genlayer-js';
import { studionet as glStudioNet, testnetBradbury as glBradbury, localnet as glLocalnet } from 'genlayer-js/chains';

// ── Custom GenLayer Chains for Wagmi ──────────────────────
export const bradbury = {
  id: 4221,
  name: 'GenLayer Bradbury Testnet',
  nativeCurrency: { name: 'GEN', symbol: 'GEN', decimals: 18 },
  rpcUrls: {
    default: { http: ['https://rpc-bradbury.genlayer.com'] },
    public: { http: ['https://rpc-bradbury.genlayer.com'] },
  },
  blockExplorers: {
    default: { name: 'GenLayer Explorer', url: 'https://explorer-bradbury.genlayer.com' }
  },
  testnet: true,
};

export const studionet = {
  id: 61998,
  name: 'GenLayer StudioNet',
  nativeCurrency: { name: 'GEN', symbol: 'GEN', decimals: 18 },
  rpcUrls: {
    default: { http: ['https://studio.genlayer.com/api'] },
    public: { http: ['https://studio.genlayer.com/api'] },
  },
  blockExplorers: {
    default: { name: 'GenLayer Explorer', url: 'https://explorer-studio.genlayer.com' }
  },
  testnet: true,
};

export const simulator = {
  id: 61999,
  name: 'GenLayer Simulator',
  nativeCurrency: { name: 'GEN', symbol: 'GEN', decimals: 18 },
  rpcUrls: {
    default: { http: ['http://127.0.0.1:4000/api'] },
    public: { http: ['http://127.0.0.1:4000/api'] },
  },
  testnet: true,
};

// ── Config Wagmi ──────────────────────────────────────────
export const config = createConfig({
  chains: [bradbury, studionet, simulator],
  connectors: [injected()],
  transports: {
    [bradbury.id]: http(),
    [studionet.id]: http(),
    [simulator.id]: http(),
  },
});

// ── Reactive State ────────────────────────────────────────
const address = ref(null);
const chainId = ref(null);
const isConnected = ref(false);
const isConnecting = ref(false);
const balance = ref(null);

// Fetch balance helper
async function fetchBalance() {
  if (!address.value) {
    balance.value = null;
    return;
  }
  try {
    let chainObj = glStudioNet;
    let rpcUrl = 'https://studio.genlayer.com/api';

    // Map chainId.value to correct GenLayer network configurations
    if (chainId.value === 4221 || chainId.value === 61997) {
      chainObj = glBradbury;
      rpcUrl = 'https://rpc-bradbury.genlayer.com';
    } else if (chainId.value === 61999) {
      chainObj = glLocalnet;
      rpcUrl = 'http://127.0.0.1:4000/api';
    }

    const client = createClient({
      chain: {
        ...chainObj,
        rpcUrls: {
          default: { http: [rpcUrl] },
          public: { http: [rpcUrl] },
        }
      },
      transport: rpcUrl
    });

    const rawBalance = await client.getBalance({ address: address.value });
    balance.value = {
      decimals: 18,
      formatted: (Number(rawBalance) / 1e18).toString(),
      symbol: 'GEN',
      value: BigInt(rawBalance)
    };
  } catch (err) {
    console.error('Failed to fetch GenLayer balance:', err);
    balance.value = null;
  }
}

// Expose refresh balance action
export async function refreshBalance() {
  await fetchBalance();
}

// Update state helper
function updateAccountState(account) {
  address.value = account.address || null;
  chainId.value = account.chainId || null;
  isConnected.value = account.isConnected || false;
  isConnecting.value = account.isConnecting || false;
  
  if (account.isConnected && account.address) {
    fetchBalance();
  } else {
    balance.value = null;
  }
}

// Watch Wagmi account state
watchAccount(config, {
  onChange(account) {
    updateAccountState(account);
  },
});

// ── Actions ───────────────────────────────────────────────
export async function connectWallet() {
  if (isConnecting.value) return;
  isConnecting.value = true;
  try {
    const result = await connect(config, {
      connector: config.connectors[0], // injected connector
    });
    const account = getAccount(config);
    updateAccountState(account);
    return result;
  } catch (err) {
    console.error('Wagmi connection failed:', err);
    throw err;
  } finally {
    isConnecting.value = false;
  }
}

export async function disconnectWallet() {
  try {
    await disconnect(config);
    address.value = null;
    chainId.value = null;
    isConnected.value = false;
    balance.value = null;
  } catch (err) {
    console.error('Wagmi disconnect failed:', err);
  }
}

// Initialize / Reconnect on boot
reconnect(config);

export const wagmiState = readonly({
  address,
  chainId,
  isConnected,
  isConnecting,
  balance,
});
