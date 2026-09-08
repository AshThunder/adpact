# AdPact — AI-Powered Agentic Commerce for the Creator Economy

> **🏆 GenLayer Agent Tank Hackathon Submission — Agentic Commerce Infrastructure Track**

AdPact is a decentralized creator sponsorship protocol built on **GenLayer Intelligent Contracts**. It replaces every human middleman in the influencer marketing stack with on-chain AI consensus — making brand-creator deals trustless, automated, and instant.

**Live on GenLayer Bradbury Testnet:** [adpact.vercel.app](https://adpact.vercel.app)

---

## 🧠 Why This Is an Agentic Commerce Problem

The $21B+ influencer marketing industry runs on mutual distrust:

- **Advertisers** pay for posts that get deleted, edited, or never published
- **Creators** wait 30–60 days to get paid for work they've already done
- **Both parties** rely on fragile manual workflows and expensive intermediary agencies

Traditional smart contracts can't solve this — they can't evaluate whether a tweet was published on time, contains the right hashtags, or was deleted after payout. This is exactly the class of **subjective, non-deterministic real-world verification** that GenLayer was built for.

AdPact is the first protocol where an **AI consensus network acts as the autonomous enforcement layer** between brand and creator — no human judge, no agency, no delay.

---

## ⚙️ How GenLayer Powers It

AdPact uses three of GenLayer's unique primitives:

| Primitive | Use in AdPact |
|-----------|---------------|
| `gl.nondet.web.render()` | Scrapes live post URLs to check if content exists and is public |
| `gl.nondet.exec_prompt()` | Runs a structured LLM prompt to evaluate post compliance against brand requirements |
| `gl.vm.run_nondet_unsafe()` | Runs leader + validator consensus so multiple nodes must independently agree before a payout triggers |

**No centralized oracle. No trusted third party. Pure on-chain AI consensus.**

---

## 🔄 The 8-Stage Collaboration State Machine

Every sponsorship deal moves through a cryptographically-enforced lifecycle:

```
OPEN_FOR_APPLICATIONS
        │
        ▼  (advertiser approves creator)
AWAITING_ESCROW_DEPOSIT
        │
        ▼  (advertiser funds escrow with budget)
DRAFT_SUBMISSION_OPEN
        │
        ▼  (creator submits post draft)
AWAITING_DRAFT_APPROVAL
        │
        ▼  (advertiser approves draft content)
AUTHORIZED_TO_PUBLISH
        │
        ▼  (creator submits live post URL)
AI_VERIFICATION_PENDING  ──► (AI fails) ──► back to AUTHORIZED_TO_PUBLISH
        │
        ▼  (AI consensus passes → 30% payout released)
RETENTION_MONITORING  ──► (post deleted) ──► BREACHED (budget refunded)
        │
        ▼  (retention period elapses + AI confirms post still live → 70% payout)
COMPLETED
```

**Nothing moves without consensus. No consensus, no payout.**

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Intelligent Contract** | Python, GenVM v4 (`py-genlayer:1jb45aa8...`) |
| **AI Execution** | `gl.nondet.exec_prompt()` + `gl.vm.run_nondet_unsafe()` |
| **Web Oracle** | `gl.nondet.web.render()` — live URL scraping |
| **Frontend** | Vue 3 + Vite, Tailwind CSS |
| **Wallet** | RainbowKit + wagmi (MetaMask, WalletConnect, Coinbase Wallet, etc.) |
| **SDK** | `genlayer-js` for `gen_call` / transaction tracking |
| **Testing** | GenLayer direct in-memory runner (pytest, no node required) |

---

## 🌐 Live Deployments

| Network | Chain ID | Contract Address |
|---------|----------|-----------------|
| **Bradbury Testnet** | `4221` | `0xeD8F38EdF8aE8Bf95A26108106050f1512852Bac` |
| **StudioNet** | `61999` | `0x17CFD6E5203AE5e2747df1880e1153543907C4df` |

---

## 🚀 Running Locally

### Prerequisites
- Node.js v18+
- Python 3.10+
- Any EVM wallet (MetaMask, Coinbase Wallet, WalletConnect, etc.)

### 1. Install & run the frontend
```bash
cd app
npm install
npm run dev
```
Opens at `http://localhost:5173`. Connect your wallet to Bradbury (`4221`) or StudioNet (`61999`).

### 2. Get test GEN tokens
- **Bradbury:** [testnet-faucet.genlayer.foundation](https://testnet-faucet.genlayer.foundation)
- **StudioNet:** [studio.genlayer.com](https://studio.genlayer.com/contracts)

---

## ✅ Running the Test Suite (No Wallet Required)

Judges and reviewers can verify the full contract lifecycle — including AI consensus and web scraping — without any wallet or deployed node, using GenLayer's **direct in-memory runner**.

```bash
pip install -r requirements.txt
pytest -v tests/direct/
```

### What the tests verify

| Test | What It Validates |
|------|-------------------|
| `test_influencer_escrow_lifecycle` | Complete 10-step flow: campaign → apply → approve → escrow → draft → AI verify → retention → withdraw |
| `test_influencer_escrow_deadline_check` | Contract correctly rejects applications after campaign deadline |
| `test_user_balance` | Virtual ledger correctly credits 30%+70% split payouts |
| `test_user_balance_no_withdraw` | Only the intended creator can withdraw their balance |

All tests run in **under 5 seconds** with zero setup beyond `pip install`.

---

## 📂 Project Structure

```
adpact/
├── contracts/
│   └── influencer_escrow.py     # GenVM v4 Intelligent Contract (717 lines)
├── app/                         # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── App.vue              # Root: landing page, nav, wallet connection
│   │   ├── components/
│   │   │   ├── Dashboard.vue    # Campaign browser, my campaigns, my applications
│   │   │   ├── CampaignDetail.vue # Full collaboration workflow UI
│   │   │   ├── CreateCampaign.vue # Campaign creation form
│   │   │   └── WalletConnect.vue  # Multi-wallet modal
│   │   └── services/
│   │       ├── genlayer.js      # GenLayer client + network management
│   │       ├── wagmi.js         # wagmi/RainbowKit wallet integration
│   │       └── contract_addresses.js # Deployed addresses per network
│   └── vercel.json              # SPA routing config
├── tests/
│   └── direct/                  # In-memory direct test suite
├── requirements.txt
└── README.md
```

---

## 🔑 Key Design Decisions

### Why the Fallback Mock?
Twitter/X blocks most public scrapers. When `gl.nondet.web.render()` returns a blocked page, the contract falls back to constructing a deterministic mock from the approved text. This ensures testnet consensus still succeeds while the real-world production path is ready for when reliable scraping APIs are integrated.

### Why a Virtual Ledger?
Instead of transferring GEN directly in each transaction (which risks reentrancy), payouts credit the creator's internal balance. Creators withdraw in a single clean transaction. This is the same pattern used by audited DeFi protocols.

### Why Two-Phase Payout (30/70)?
The split incentivizes honest behavior at both stages: initial publication (30% upfront) and continued post retention (70% after retention check). If the creator deletes the post during the retention period, the remaining 70% is refunded to the advertiser.

---

## 📜 License
MIT — see [LICENSE](LICENSE)

---

**AdPact** · Built for the GenLayer Agent Tank Hackathon · Agentic Commerce Infrastructure Track  
[github.com/AshThunder/adpact](https://github.com/AshThunder/adpact)
