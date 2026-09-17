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

  // ─── Demo Mode Simulation ───────────────────────────────────
  async _simulateIfDemo(onTxHash) {
    if (typeof window !== 'undefined' && window.location.search.includes('demo=true')) {
      const mockHash = '0x' + Array.from({length: 64}, () => Math.floor(Math.random()*16).toString(16)).join('');
      if (onTxHash) onTxHash(mockHash);
      await new Promise(r => setTimeout(r, 1000));
      return { status: 'ACCEPTED', transactionHash: mockHash, consensus_data: { leader_receipt: [{ execution_result: 'SUCCESS' }] } };
    }
    return null;
  }

  // ─── Fee Estimation ─────────────────────────────────────────
  // Studio Next (Consensus v0.6) requires a non-zero fee deposit
  // on every write transaction.  We estimate fees once per write
  // and merge them into the writeContract options.

  async _estimateFees(client) {
    try {
      const estimate = await client.estimateTransactionFees();
      return {
        distribution: estimate.distribution,
        feeValue: estimate.feeValue,
      };
    } catch (err) {
      console.warn("Fee estimation failed, using fallback:", err);
      // Fallback: generous static fee (≈0.001 GEN) to avoid FeeValueMustBeNonZero
      return {
        feeValue: 1_000_000_000_000_000n,
      };
    }
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
    const demoSim = await this._simulateIfDemo(onTxHash);
    if (demoSim) return demoSim;

    // Sync MetaMask & GenLayer snap connection before execution
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

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
      value: 0n,
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async applyToCampaign(campaignId, twitterHandle, proposalMessage, onTxHash = null) {
    const demoSim = await this._simulateIfDemo(onTxHash);
    if (demoSim) return demoSim;

    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "apply_to_campaign",
      args: [campaignId, twitterHandle, proposalMessage],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async approveCreator(campaignId, creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "approve_creator",
      args: [campaignId, creatorAddress],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async depositEscrow(campaignId, creatorAddress, amount, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "deposit_escrow",
      args: [campaignId, creatorAddress],
      value: BigInt(amount),
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async submitDraft(campaignId, draftText, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "submit_draft",
      args: [campaignId, draftText],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async approveDraft(campaignId, creatorAddress, approved, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "approve_draft",
      args: [campaignId, creatorAddress, approved],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async submitLivePost(campaignId, liveTweetUrl, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "submit_live_post",
      args: [campaignId, liveTweetUrl],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async verifyLivePost(campaignId, creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "verify_live_post",
      args: [campaignId, creatorAddress],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash, 20);
  }

  async verifyRetention(campaignId, creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "verify_retention",
      args: [campaignId, creatorAddress],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash, 20);
  }

  async cancelCollaboration(campaignId, creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "cancel_collaboration",
      args: [campaignId, creatorAddress],
      fees,
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
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "withdraw_balance",
      args: [],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  // ─── X Profile & Reputation Methods ────────────────────────

  async getCreatorProfile(creatorAddress) {
    try {
      const raw = await this.client.readContract({
        address: this.contractAddress,
        functionName: "get_creator_profile",
        args: [creatorAddress],
      });
      return raw && (typeof raw === "object" || typeof raw.entries === "function")
        ? this._mapToObj(raw)
        : null;
    } catch (e) {
      console.warn("getCreatorProfile error:", e);
      return null;
    }
  }

  async getAllProfiles() {
    try {
      const raw = await this.client.readContract({
        address: this.contractAddress,
        functionName: "get_all_profiles",
        args: [],
      });
      const profiles = {};
      if (raw && typeof raw.entries === "function") {
        for (const [addr, data] of raw.entries()) {
          profiles[addr.toLowerCase()] = this._mapToObj(data);
        }
      } else if (raw && typeof raw === "object") {
        for (const [addr, data] of Object.entries(raw)) {
          profiles[addr.toLowerCase()] = data.entries ? this._mapToObj(data) : data;
        }
      }
      return profiles;
    } catch (e) {
      console.warn("getAllProfiles error:", e);
      return {};
    }
  }

  async requestXChallenge(twitterHandle, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "request_x_challenge",
      args: [twitterHandle],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async verifyXAccount(tweetUrl = "", onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "verify_x_account",
      args: [tweetUrl],
      fees,
    });
    if (onTxHash) onTxHash(txHash);
    return this._waitFinalized(txHash);
  }

  async getPendingChallenge(address) {
    try {
      const result = await this.client.readContract({
        account: this.account,
        address: this.contractAddress,
        functionName: "get_pending_challenge",
        args: [address],
      });
      return result && (typeof result === "object" || typeof result.entries === "function")
        ? this._mapToObj(result)
        : {};
    } catch (e) {
      console.warn("getPendingChallenge error:", e);
      return {};
    }
  }

  async getHandleOwner(twitterHandle) {
    try {
      const result = await this.client.readContract({
        account: this.account,
        address: this.contractAddress,
        functionName: "get_handle_owner",
        args: [twitterHandle],
      });
      return result || "";
    } catch (e) {
      console.warn("getHandleOwner error:", e);
      return "";
    }
  }

  async auditCreatorReputation(creatorAddress, onTxHash = null) {
    const activeClient = await syncSnapConnection();
    const fees = await this._estimateFees(activeClient);

    const txHash = await activeClient.writeContract({
      address: this.contractAddress,
      functionName: "audit_creator_reputation",
      args: [creatorAddress],
      fees,
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

