import { getGenLayerClient, syncSnapConnection } from "../services/genlayer.js";

class InfluencerEscrow {
  contractAddress;
  accountAddress;

  constructor(contractAddress, accountAddress = null) {
    this.contractAddress = contractAddress;
    this.accountAddress = accountAddress;
  }

  updateAccount(accountAddress) {
    this.accountAddress = accountAddress;
  }

  get client() {
    return getGenLayerClient(this.accountAddress);
  }

  // ─── Read Methods ───────────────────────────────────────────

  async getCampaigns() {
    const raw = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_campaigns",
      args: [],
    });
    // raw is a Map or Object; convert to plain object array
    const campaigns = [];
    if (raw && typeof raw.entries === "function") {
      for (const [id, data] of raw.entries()) {
        campaigns.push({ id, ...this._mapToObj(data) });
      }
    } else if (raw && typeof raw === "object") {
      for (const [id, data] of Object.entries(raw)) {
        campaigns.push({
          id,
          ...(data.entries ? this._mapToObj(data) : data),
        });
      }
    }
    return campaigns;
  }

  async getApplications(campaignId) {
    const raw = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_applications",
      args: [campaignId],
    });
    const apps = [];
    if (raw && typeof raw.entries === "function") {
      for (const [addr, data] of raw.entries()) {
        apps.push({ creator: addr, ...this._mapToObj(data) });
      }
    } else if (raw && typeof raw === "object") {
      for (const [addr, data] of Object.entries(raw)) {
        apps.push({
          creator: addr,
          ...(data.entries ? this._mapToObj(data) : data),
        });
      }
    }
    return apps;
  }

  async getCollaborations(campaignId) {
    const raw = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_collaborations",
      args: [campaignId],
    });
    const collabs = [];
    if (raw && typeof raw.entries === "function") {
      for (const [addr, data] of raw.entries()) {
        collabs.push({ creator: addr, ...this._mapToObj(data) });
      }
    } else if (raw && typeof raw === "object") {
      for (const [addr, data] of Object.entries(raw)) {
        collabs.push({
          creator: addr,
          ...(data.entries ? this._mapToObj(data) : data),
        });
      }
    }
    return collabs;
  }

  async getUserApplications(accountAddress) {
    const raw = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_user_applications",
      args: [accountAddress],
    });
    // raw is { campaign_id: { status, collaboration } }
    const results = {};
    if (raw && typeof raw.entries === "function") {
      for (const [campId, data] of raw.entries()) {
        results[campId] = data.entries ? this._mapToObj(data) : data;
      }
    } else if (raw && typeof raw === "object") {
      for (const [campId, data] of Object.entries(raw)) {
        results[campId] = data.entries ? this._mapToObj(data) : data;
      }
    }
    return results;
  }

  // ─── Write Methods ──────────────────────────────────────────

  async createCampaign({
    title,
    description,
    attoBudgetPerCreator,
    maxCreators,
    platform,
    requiredHashtags,
    requiredKeywords,
    retentionDurationSeconds,
    postingDeadline,
    paymentStructure,
  }, onTxHash = null) {
    // Sync MetaMask & GenLayer snap connection before execution
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "create_campaign",
      args: [
        title,
        description,
        attoBudgetPerCreator,
        maxCreators,
        platform,
        JSON.stringify(requiredHashtags),
        JSON.stringify(requiredKeywords),
        retentionDurationSeconds,
        postingDeadline,
        JSON.stringify(paymentStructure),
      ],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async applyToCampaign(campaignId, twitterHandle, proposalMessage, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "apply_to_campaign",
      args: [campaignId, twitterHandle, proposalMessage],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async approveCreator(campaignId, creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "approve_creator",
      args: [campaignId, creatorAddress],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async depositEscrow(campaignId, creatorAddress, amount, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "deposit_escrow",
      args: [campaignId, creatorAddress],
      value: BigInt(amount),
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async submitDraft(campaignId, draftText, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "submit_draft",
      args: [campaignId, draftText],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async approveDraft(campaignId, creatorAddress, approved, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "approve_draft",
      args: [campaignId, creatorAddress, approved],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async submitLivePost(campaignId, liveTweetUrl, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "submit_live_post",
      args: [campaignId, liveTweetUrl],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async verifyLivePost(campaignId, creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "verify_live_post",
      args: [campaignId, creatorAddress],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash, 20);
  }

  async verifyRetention(campaignId, creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "verify_retention",
      args: [campaignId, creatorAddress],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash, 20);
  }

  async cancelCollaboration(campaignId, creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "cancel_collaboration",
      args: [campaignId, creatorAddress],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash, 20);
  }

  // ─── Virtual Escrow Balance Methods ───────────────────────

  async getBalance(accountAddress) {
    const raw = await this.client.readContract({
      address: this.contractAddress,
      functionName: "get_balance",
      args: [accountAddress],
    });
    return raw ? raw.toString() : "0";
  }

  async withdrawBalance(onTxHash = null) {
    const activeClient = await syncSnapConnection();

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "withdraw_balance",
      args: [],
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  // ─── Helpers ────────────────────────────────────────────────

  async _waitFinalized(txHash, retries = 60) {
    const receipt = await this.client.waitForTransactionReceipt({
      hash: txHash,
      status: "ACCEPTED",
      interval: 5000,
      retries,
    });
    return receipt;
  }

  _mapToObj(mapOrObj) {
    if (!mapOrObj) return {};
    if (typeof mapOrObj.entries === "function") {
      const obj = {};
      for (const [k, v] of mapOrObj.entries()) {
        obj[k] = v;
      }
      return obj;
    }
    return mapOrObj;
  }
}

export default InfluencerEscrow;
