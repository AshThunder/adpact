import { ref, watch } from 'vue';
import { createClient } from "genlayer-js";
import { localnet, studionet, testnetBradbury } from "genlayer-js/chains";
import { wagmiState, connectWallet, config as wagmiConfig } from "./wagmi.js";
import { switchChain } from "@wagmi/core";

// ── Network Definitions ──────────────────────────────────
export const NETWORKS = {
  studionet: {
    key: 'studionet',
    name: 'StudioNet',
    chain: studionet,
    rpcUrl: 'https://studio.genlayer.com/api',
    chainId: 61999,
    wagmiId: 61999,
  },
  bradbury: {
    key: 'bradbury',
    name: 'Bradbury Testnet',
    chain: testnetBradbury,
    rpcUrl: 'https://rpc-bradbury.genlayer.com',
    chainId: 4221,
    wagmiId: 4221, // Wagmi ID used for Bradbury
  },
  simulator: {
    key: 'simulator',
    name: 'Simulator (Localnet)',
    chain: localnet,
    rpcUrl: 'http://127.0.0.1:4000/api',
    chainId: 61999,
    wagmiId: 61999,
  }
};

// ── Reactive Active Network ──────────────────────────────
let savedNetwork = localStorage.getItem("selectedNetwork") || "studionet";
if (savedNetwork === "simulator") savedNetwork = "studionet";
export const selectedNetwork = ref(savedNetwork);

export function setNetwork(networkKey) {
  if (!NETWORKS[networkKey] || networkKey === 'simulator') return;
  selectedNetwork.value = networkKey;
  localStorage.setItem("selectedNetwork", networkKey);
}

// ── Client Factory ───────────────────────────────────────
export function getGenLayerClient(accountAddress = null) {
  const net = NETWORKS[selectedNetwork.value];

  const clientConfig = {
    chain: {
      ...net.chain,
      rpcUrls: {
        default: { http: [net.rpcUrl] },
        public: { http: [net.rpcUrl] },
      }
    },
    transport: net.rpcUrl,
    ...(accountAddress ? { account: accountAddress } : {}),
  };

  return createClient(clientConfig);
}

// ── Connect & Snap Switcher helper ───────────────────────
export async function syncSnapConnection() {
  if (!window.ethereum) {
    throw new Error("MetaMask is required to connect to GenLayer");
  }

  const net = NETWORKS[selectedNetwork.value];

  // 1. Switch network in Wagmi / MetaMask if needed
  if (wagmiState.isConnected && wagmiState.chainId !== net.wagmiId) {
    try {
      await switchChain(wagmiConfig, { chainId: net.wagmiId });
    } catch (err) {
      console.warn("Wagmi switchChain error, falling back to manual add:", err);
      // Attempt manual add
      try {
        await window.ethereum.request({
          method: 'wallet_addEthereumChain',
          params: [
            {
              chainId: `0x${net.wagmiId.toString(16)}`,
              chainName: net.name,
              rpcUrls: [net.rpcUrl],
              nativeCurrency: {
                name: "GEN",
                symbol: "GEN",
                decimals: 18,
              },
            },
          ],
        });
        await window.ethereum.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: `0x${net.wagmiId.toString(16)}` }],
        });
      } catch (addError) {
        console.warn("Failed to manually add/switch network:", addError);
        // Continue anyway, maybe the write will succeed if the wallet handles it
      }
    }
  }

  // 2. Connect client and register/switch snap network
  const client = getGenLayerClient(wagmiState.address);

  // Map our key to snap connect's network argument:
  // snap connect accepts 'studionet', 'testnetBradbury', 'localnet'
  const snapNetworkKey =
    selectedNetwork.value === 'bradbury' ? 'testnetBradbury' :
      selectedNetwork.value === 'simulator' ? 'localnet' : 'studionet';

  console.log(`Connecting GenLayer Snap to network: ${snapNetworkKey}`);
  try {
    await client.connect(snapNetworkKey);
  } catch (err) {
    console.warn("GenLayer Snap connect error:", err);
    // If the error is about chain not supported or snaps not supported, we can fallback to standard EVM
    const msg = err.message || err.toString();
    if (msg.includes("not supported") || msg.includes("wallet_getSnaps")) {
      console.log("Snap or chain switch not supported by wallet, proceeding with standard EVM wallet connection.");
    } else {
      // For other errors, we still continue and hope the standard EVM transaction works
      console.log("Proceeding with standard EVM fallback.");
    }
  }

  return client;
}
